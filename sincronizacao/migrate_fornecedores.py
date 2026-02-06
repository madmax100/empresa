import pyodbc
import psycopg2
import pandas as pd
import re
from datetime import datetime
from config import PG_CONFIG, ACCESS_PASSWORD, CADASTROS_DB # ou o DB específico

def clean_string(value):
    return str(value).strip() if value and pd.notna(value) else None

def clean_cpf_cnpj(doc):
    return re.sub(r'[^\d]', '', str(doc)) if doc and pd.notna(doc) else None

def clean_phone(phone):
    return re.sub(r'[^\d]', '', str(phone)) if phone and pd.notna(phone) else None

def get_existing_fornecedores(pg_cursor):
    pg_cursor.execute("SELECT id FROM fornecedores")
    return {row[0] for row in pg_cursor.fetchall()}

def migrate_fornecedores():
    try:
        access_path = CADASTROS_DB
        conn_str = (
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={access_path};'
            'PWD=010182;'
        )

        with pyodbc.connect(conn_str) as access_conn, \
             psycopg2.connect(**PG_CONFIG) as pg_conn:
            
            pg_cursor = pg_conn.cursor()
            existing_fornecedores = get_existing_fornecedores(pg_cursor)

            query = "SELECT * FROM Fornecedores ORDER BY codigo"
            df = pd.read_sql(query, access_conn)

            insert_sql = """
                INSERT INTO fornecedores (
                    id, tipo_pessoa, nome, cpf_cnpj, rg_ie,
                    endereco, bairro, cidade, estado, cep,
                    telefone, email, contato_nome, contato_telefone,
                    data_cadastro, ativo
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
                    contato_nome = EXCLUDED.contato_nome,
                    contato_telefone = EXCLUDED.contato_telefone,
                    data_cadastro = EXCLUDED.data_cadastro,
                    ativo = EXCLUDED.ativo
            """

            insercoes = atualizacoes = erros = 0

            for _, row in df.iterrows():
                try:
                    fornecedor_id = int(row['codigo'])
                    dados = (
                        fornecedor_id,
                        'J',
                        clean_string(row['nome']),
                        clean_cpf_cnpj(row['cgc']),
                        clean_string(row['cgf']),
                        clean_string(row['endereco']),
                        clean_string(row['bairro']),
                        clean_string(row['cidade']),
                        clean_string(row['uf']),
                        clean_string(row['cep']),
                        clean_phone(row['fone']),
                        clean_string(row['email']),
                        clean_string(row['contato']),
                        clean_phone(row['celular']),
                        row['datacadastro'] if pd.notna(row['datacadastro']) else datetime.now(),
                        True
                    )

                    pg_cursor.execute(insert_sql, dados)
                    pg_conn.commit()

                    if fornecedor_id in existing_fornecedores:
                        atualizacoes += 1
                    else:
                        insercoes += 1

                except Exception as e:
                    erros += 1
                    print(f"Erro ao processar fornecedor {row['codigo']}: {str(e)}")
                    pg_conn.rollback()

            pg_cursor.execute("SELECT setval('fornecedores_id_seq', COALESCE((SELECT MAX(id) FROM fornecedores), 1), true);")
            pg_conn.commit()

            print(f"\nFornecedores inseridos: {insercoes}")
            print(f"Fornecedores atualizados: {atualizacoes}")
            print(f"Erros: {erros}")

            return True

    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        return False