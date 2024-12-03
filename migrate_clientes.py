import pyodbc
import psycopg2
import pandas as pd
import re
from datetime import datetime
from decimal import Decimal


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
    """Converte valor para decimal, tratando casos especiais"""
    if pd.isna(value) or value is None:
        return Decimal('0.00')
    try:
        # Remove caracteres não numéricos exceto ponto e vírgula
        clean_value = re.sub(r'[^\d.,]', '', str(value))
        # Substitui vírgula por ponto
        clean_value = clean_value.replace(',', '.')
        return Decimal(clean_value)
    except:
        return Decimal('0.00')

def limpar_tabelas(pg_conn):
    try:
        cursor = pg_conn.cursor()
        
        print("\nIniciando limpeza das tabelas...")
        
        # Desabilitar verificação de chaves estrangeiras
        cursor.execute("SET session_replication_role = 'replica';")
        
        # Lista de tabelas para limpar (na ordem correta)
        tabelas = [
            'contas_receber',
            'notas_fiscais_saida',
            'contratos_locacao',
            'clientes'
        ]
        
        for tabela in tabelas:
            try:
                print(f"\nVerificando tabela {tabela}...")
                cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                qtd_antes = cursor.fetchone()[0]
                print(f"Registros encontrados em {tabela}: {qtd_antes}")
                
                if qtd_antes > 0:
                    print(f"Limpando tabela {tabela}...")
                    cursor.execute(f"TRUNCATE TABLE {tabela} CASCADE")
                    pg_conn.commit()
                    print(f"Tabela {tabela} limpa com sucesso!")
                
            except Exception as e:
                print(f"Erro ao limpar tabela {tabela}: {str(e)}")
                pg_conn.rollback()
                raise
        
        cursor.execute("SET session_replication_role = 'origin';")
        pg_conn.commit()
        
        print("\nLimpeza concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro durante a limpeza: {str(e)}")
        pg_conn.rollback()
        return False

def criar_tabela_clientes(pg_cursor):
    """Cria a tabela clientes no PostgreSQL"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY,  -- Alterado para usar o CODCLIENTE como id
        tipo_pessoa CHAR(1),
        nome VARCHAR(100) NOT NULL,
        cpf_cnpj VARCHAR(14),
        rg_ie VARCHAR(20),
        data_nascimento DATE,
        endereco VARCHAR(100),
        numero VARCHAR(10),
        complemento VARCHAR(50),
        bairro VARCHAR(50),
        cidade VARCHAR(50),
        estado CHAR(2),
        cep VARCHAR(8),
        telefone VARCHAR(20),
        email VARCHAR(100),
        limite_credito DECIMAL(10,2),
        data_cadastro TIMESTAMP,
        ativo BOOLEAN DEFAULT true,
        contato VARCHAR(50)
    );

    CREATE INDEX IF NOT EXISTS idx_clientes_nome ON clientes (nome);
    CREATE INDEX IF NOT EXISTS idx_clientes_cpf_cnpj ON clientes (cpf_cnpj);
    CREATE INDEX IF NOT EXISTS idx_clientes_cidade ON clientes (cidade);
    """
    pg_cursor.execute(create_table_sql)

def migrar_clientes():
    pg_config = {
        'dbname': 'c3mcopiasdb2',
        'user': 'cirilomax',
        'password': '226cmm100',
        'host': 'localhost',
        'port': '5432'
    }

    db_path = r"C:\Users\Cirilo\Documents\c3mcopias\Bancos\cadastros\Cadastros.mdb"
    
    try:
        # Conexões
        print("Conectando aos bancos de dados...")
        conn_str = (
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={db_path};'
            'PWD=010182;'
        )
        access_conn = pyodbc.connect(conn_str)
        pg_conn = psycopg2.connect(**pg_config)
        
        # Limpar tabelas antes da importação
        if not limpar_tabelas(pg_conn):
            raise Exception("Falha na limpeza das tabelas. Abortando importação.")

        pg_cursor = pg_conn.cursor()
        
        # Criar/atualizar estrutura da tabela
        print("\nVerificando estrutura da tabela...")
        criar_tabela_clientes(pg_cursor)
        pg_conn.commit()

    
        # Busca dados do Access
        print("\nBuscando dados do Access...")
        access_cursor = access_conn.cursor()
        access_cursor.execute("""
            SELECT CODCLIENTE, NOME, ENDERECO, BAIRRO, CIDADE, UF, CEP, 
                   FONE, [CPF/CGC] as CPF_CGC, DATACADASTRO, CONTATO, [RG/IE] as RG_IE, 
                   EMAIL, LIMITE
            FROM Clientes 
            ORDER BY CODCLIENTE
        """)

        # Definição do SQL de inserção
        insert_sql = """
            INSERT INTO clientes (
                id, tipo_pessoa, nome, cpf_cnpj, rg_ie, 
                endereco, bairro, cidade, estado, cep,
                telefone, email, limite_credito, data_cadastro, 
                ativo, contato
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
        """

        # Processo de migração
        contador = 0
        erros = 0
        
        print("\nIniciando migração dos clientes...")
        
        while True:
            rows = access_cursor.fetchmany(1000)
            if not rows:
                break
            
            for row in rows:
                try:
                    # Debug para verificar os dados
                    #print(f"\nProcessando cliente ID: {row[0]}")
                    
                    # Determinar tipo de pessoa baseado no CPF/CNPJ
                    cpf_cnpj = clean_cpf_cnpj(row[8])  # CPF_CGC
                    tipo_pessoa = 'J' if cpf_cnpj and len(cpf_cnpj) > 11 else 'F'
                    
                    # Preparar data de cadastro
                    data_cadastro = row[9] if row[9] else datetime.now()
                    
                    # Preparar limite de crédito
                    limite = clean_decimal(row[13])
                    
                    dados = (
                        int(row[0]),                # id (CODCLIENTE)
                        tipo_pessoa,                # tipo_pessoa
                        clean_string(row[1]),       # nome (NOME)
                        cpf_cnpj,                   # cpf_cnpj (CPF_CGC)
                        clean_string(row[11]),      # rg_ie (RG_IE)
                        clean_string(row[2]),       # endereco (ENDERECO)
                        clean_string(row[3]),       # bairro (BAIRRO)
                        clean_string(row[4]),       # cidade (CIDADE)
                        clean_string(row[5]),       # estado (UF)
                        clean_string(row[6]),       # cep (CEP)
                        clean_phone(row[7]),        # telefone (FONE)
                        clean_string(row[12]),      # email (EMAIL)
                        limite,                     # limite_credito (LIMITE)
                        data_cadastro,              # data_cadastro (DATACADASTRO)
                        True,                       # ativo
                        clean_string(row[10])       # contato (CONTATO)
                    )
                    
                    # Debug dos dados preparados
                    #print(f"Dados preparados: {dados}")
                    
                    pg_cursor.execute(insert_sql, dados)
                    pg_conn.commit()  # Commit após cada inserção
                    contador += 1
                    
                    if contador % 100 == 0:
                        print(f"Migrados {contador} clientes...")
                
                except Exception as e:
                    erros += 1
                    print(f"Erro ao migrar cliente {row[0]}: {str(e)}")
                    print(f"Dados que causaram erro: {row}")
                    pg_conn.rollback()
                    continue

        print("\nMigração concluída!")
        print(f"Total de clientes migrados: {contador}")
        print(f"Total de erros: {erros}")
        
        # Verificar sequência se necessário
        pg_cursor.execute("""
            SELECT setval(pg_get_serial_sequence('clientes', 'id'), 
                         (SELECT MAX(id) FROM clientes));
        """)
        pg_conn.commit()
        
    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        if 'pg_conn' in locals():
            pg_conn.rollback()
    finally:
        if 'access_conn' in locals():
            access_conn.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == "__main__":
    print("=== MIGRAÇÃO DE CLIENTES ===")
    print("Início:", datetime.now())
    migrar_clientes()
    print("Fim:", datetime.now())
