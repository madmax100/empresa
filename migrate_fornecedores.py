
import pyodbc
import psycopg2
import pandas as pd
import re
from datetime import datetime

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

def migrate_fornecedores():
    pg_config = {
        'dbname': 'c3mcopiasdb2',
        'user': 'cirilomax',
        'password': '226cmm100',
        'host': 'localhost',
        'port': '5432'
    }

    access_path = r"C:\Users\Cirilo\Documents\c3mcopias\Bancos\Cadastros\Cadastros.mdb"
    
    try:
        # Conexões
        print("Conectando aos bancos de dados...")
        conn_str = (
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={access_path};'
            'PWD=010182;'
        )
        access_conn = pyodbc.connect(conn_str)
        pg_conn = psycopg2.connect(**pg_config)
        pg_cursor = pg_conn.cursor()

        # Desabilitar restrições temporariamente
        pg_cursor.execute("SET session_replication_role = 'replica';")
        pg_conn.commit()

        # Limpar tabela existente
        print("Limpando tabela de fornecedores...")
        pg_cursor.execute("TRUNCATE TABLE fornecedores CASCADE;")
        pg_conn.commit()
        
        # Ler dados do Access
        print("Lendo dados do Access...")
        query = "SELECT * FROM Fornecedores ORDER BY codigo"
        df = pd.read_sql(query, access_conn)
        
        print(f"Total de fornecedores encontrados: {len(df)}")
        
        # Migrar fornecedores
        total = len(df)
        migrados = 0
        erros = 0
        
        for _, row in df.iterrows():
            try:
                fornecedor_id = int(row['codigo'])
                
                pg_cursor.execute("""
                    INSERT INTO fornecedores (
                        id, tipo_pessoa, nome, cpf_cnpj, rg_ie,
                        endereco, numero, complemento, bairro, cidade, estado, cep,
                        telefone, email, contato_nome, contato_telefone,
                        data_cadastro, ativo
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    fornecedor_id,
                    'J',
                    clean_string(row['nome']),
                    clean_cpf_cnpj(row['cgc']),
                    clean_string(row['cgf']),
                    clean_string(row['endereco']),
                    None,
                    None,
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
                ))
                
                # Commit após cada inserção
                pg_conn.commit()
                
                migrados += 1
                if migrados % 50 == 0:
                    print(f"Migrados {migrados} de {total} fornecedores...")
                
            except Exception as e:
                erros += 1
                print(f"Erro ao migrar fornecedor {row['codigo']}: {str(e)}")
                pg_conn.rollback()  # Rollback em caso de erro
                continue

        # Reabilitar restrições
        pg_cursor.execute("SET session_replication_role = 'origin';")
        pg_conn.commit()
        
        print("\nMigração concluída!")
        print(f"Total de fornecedores migrados: {migrados}")
        print(f"Total de erros: {erros}")
        
        # Verificar sequência
        pg_cursor.execute("""
            SELECT setval('fornecedores_id_seq', 
                         COALESCE((SELECT MAX(id) FROM fornecedores), 1), 
                         true);
        """)
        pg_conn.commit()
        
    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        if 'pg_conn' in locals():
            pg_conn.rollback()
        raise
    finally:
        if 'access_conn' in locals():
            access_conn.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == "__main__":
    print("=== MIGRAÇÃO DE FORNECEDORES ===")
    print("Início:", datetime.now())
    migrate_fornecedores()
    print("Fim:", datetime.now())
