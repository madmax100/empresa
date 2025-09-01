import pyodbc
import psycopg2
import pandas as pd
import re
from datetime import datetime
from decimal import Decimal
from config import PG_CONFIG, ACCESS_PASSWORD, CADASTROS_DB # ou o DB específico

def clean_string(value):
    if pd.isna(value) or value is None:
        return None
    return str(value).strip()

def clean_cpf_cnpj(doc):
    if pd.isna(doc) or doc is None:
        return None
    return re.sub(r'[^\d]', '', str(doc))

def clean_phone(phone):
    if pd.isna(phone) or phone is None:
        return None
    return re.sub(r'[^\d]', '', str(phone))

def clean_decimal(value):
    if pd.isna(value) or value is None:
        return Decimal('0.00')
    try:
        clean_value = re.sub(r'[^\d.,]', '', str(value))
        clean_value = clean_value.replace(',', '.')
        return Decimal(clean_value)
    except:
        return Decimal('0.00')

def get_existing_clients(pg_cursor):
    """Recupera os clientes existentes no PostgreSQL"""
    pg_cursor.execute("SELECT id, data_cadastro FROM clientes")
    return {row[0]: row[1] for row in pg_cursor.fetchall()}

def get_access_clients(access_cursor):
    """Recupera os clientes do Access"""
    access_cursor.execute("""
        SELECT CODCLIENTE, NOME, ENDERECO, BAIRRO, CIDADE, UF, CEP, 
               FONE, [CPF/CGC] as CPF_CGC, DATACADASTRO, CONTATO, [RG/IE] as RG_IE, 
               EMAIL, LIMITE
        FROM Clientes 
        ORDER BY CODCLIENTE
    """)
    return access_cursor.fetchall()

def process_client_row(row):
    """Processa uma linha de cliente do Access"""
    cpf_cnpj = clean_cpf_cnpj(row[8])
    tipo_pessoa = 'J' if cpf_cnpj and len(cpf_cnpj) > 11 else 'F'
    data_cadastro = row[9] if row[9] else datetime.now()
    limite = clean_decimal(row[13])
    
    return (
        int(row[0]),                # id
        tipo_pessoa,                # tipo_pessoa
        clean_string(row[1]),       # nome
        cpf_cnpj,                   # cpf_cnpj
        clean_string(row[11]),      # rg_ie
        clean_string(row[2]),       # endereco
        clean_string(row[3]),       # bairro
        clean_string(row[4]),       # cidade
        clean_string(row[5]),       # estado
        clean_string(row[6]),       # cep
        clean_phone(row[7]),        # telefone
        clean_string(row[12]),      # email
        limite,                     # limite_credito
        data_cadastro,              # data_cadastro
        True,                       # ativo
        clean_string(row[10])       # contato
    )

def migrar_clientes():
    try:
        db_path = r"C:\Users\Cirilo\Documents\c3mcopias\Bancos\cadastros\Cadastros.mdb"
        conn_str = (
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={db_path};'
            'PWD=010182;'
        )
        
        with pyodbc.connect(conn_str) as access_conn, \
             psycopg2.connect(**PG_CONFIG) as pg_conn:
            
            pg_cursor = pg_conn.cursor()
            access_cursor = access_conn.cursor()

            # Obtém clientes existentes e do Access
            existing_clients = get_existing_clients(pg_cursor)
            access_rows = get_access_clients(access_cursor)

            insert_sql = """
                INSERT INTO clientes (
                    id, tipo_pessoa, nome, cpf_cnpj, rg_ie, 
                    endereco, bairro, cidade, estado, cep,
                    telefone, email, limite_credito, data_cadastro, 
                    ativo, contato
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    tipo_pessoa = EXCLUDED.tipo_pessoa,
                    nome = EXCLUDED.nome,
                    cpf_cnpj = EXCLUDED.cpf_cnpj,
                    rg_ie = EXCLUDED.rg_ie,
                    endereco = EXCLUDED.endereco,
                    bairro = EXCLUDED.bairro,
                    cidade = EXCLUDED.cidade,
                    estado = EXCLUDED.estado,
                    cep = EXCLUDED.cep,
                    telefone = EXCLUDED.telefone,
                    email = EXCLUDED.email,
                    limite_credito = EXCLUDED.limite_credito,
                    data_cadastro = EXCLUDED.data_cadastro,
                    ativo = EXCLUDED.ativo,
                    contato = EXCLUDED.contato
            """

            contador_insercoes = 0
            contador_atualizacoes = 0
            erros = 0

            for row in access_rows:
                try:
                    client_id = int(row[0])
                    dados = process_client_row(row)
                    
                    if client_id in existing_clients:
                        contador_atualizacoes += 1
                    else:
                        contador_insercoes += 1
                        
                    pg_cursor.execute(insert_sql, dados)
                    pg_conn.commit()

                    if (contador_insercoes + contador_atualizacoes) % 100 == 0:
                        print(f"Processados {contador_insercoes + contador_atualizacoes} clientes...")
                
                except Exception as e:
                    erros += 1
                    print(f"Erro ao processar cliente {row[0]}: {str(e)}")
                    pg_conn.rollback()

            # Atualiza a sequence
            pg_cursor.execute("""
                SELECT setval(pg_get_serial_sequence('clientes', 'id'), 
                            (SELECT MAX(id) FROM clientes));
            """)
            pg_conn.commit()

            print("\nMigração concluída!")
            print(f"Clientes inseridos: {contador_insercoes}")
            print(f"Clientes atualizados: {contador_atualizacoes}")
            print(f"Erros: {erros}")

            return True

    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        return False