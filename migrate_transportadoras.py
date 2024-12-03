import pyodbc
import psycopg2
from datetime import datetime
import re

def clean_string(value):
    if value is None:
        return None
    return str(value).strip()

def clean_cpf_cnpj(doc):
    if doc is None:
        return None
    return re.sub(r'[^\d]', '', str(doc))

def clean_phone(phone):
    if phone is None:
        return None
    return re.sub(r'[^\d]', '', str(phone))

def limpar_tabelas(pg_conn):
    try:
        cursor = pg_conn.cursor()
        
        print("\nIniciando limpeza das tabelas...")
        cursor.execute("SET session_replication_role = 'replica';")
        
        tabelas = [
            'fretes',
            'transportadoras'
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

def migrar_transportadoras():
    pg_config = {
        'dbname': 'c3mcopiasdb2',
        'user': 'cirilomax',
        'password': '226cmm100',
        'host': 'localhost',
        'port': '5432'
    }

    db_path = r"C:\Users\Cirilo\Documents\empresa\Bancos\cadastros\Cadastros.mdb"
    
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
        
        # Limpar tabelas
        if not limpar_tabelas(pg_conn):
            raise Exception("Falha na limpeza das tabelas. Abortando importação.")

        pg_cursor = pg_conn.cursor()
        
        # Busca dados do Access
        print("\nBuscando dados do Access...")
        access_cursor = access_conn.cursor()
        access_cursor.execute("""
            SELECT codigo, nome, endereco, bairro, cidade, 
                   cep, fone, celular, Contato, Região, 
                   CNPJ, UF, IE
            FROM Transportadoras 
            ORDER BY codigo
        """)

        # SQL de inserção
        insert_sql = """
            INSERT INTO transportadoras (
                id, razao_social, nome, cnpj, ie,
                endereco, bairro, cidade, estado, cep,
                fone, celular, email, contato,
                data_cadastro, ativo
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
        """

        # Processo de migração
        contador = 0
        erros = 0
        
        print("\nIniciando migração das transportadoras...")
        
        while True:
            rows = access_cursor.fetchmany(1000)
            if not rows:
                break
            
            for row in rows:
                try:
                    print(f"\nProcessando transportadora ID: {row[0]}")
                    
                    dados = (
                        int(row[0]),                # id (codigo)
                        clean_string(row[1]),       # razao_social
                        clean_string(row[1]),       # nome (mesmo que razao_social)
                        clean_cpf_cnpj(row[10]),    # cnpj
                        clean_string(row[12]),      # ie
                        clean_string(row[2]),       # endereco
                        clean_string(row[3]),       # bairro
                        clean_string(row[4]),       # cidade
                        clean_string(row[11]),      # estado (UF)
                        clean_string(row[5]),       # cep
                        clean_phone(row[6]),        # fone
                        clean_phone(row[7]),        # celular
                        None,                       # email (não tem no Access)
                        clean_string(row[8]),       # contato
                        datetime.now(),             # data_cadastro
                        True                        # ativo
                    )
                    
                    pg_cursor.execute(insert_sql, dados)
                    pg_conn.commit()
                    contador += 1
                    
                    print(f"Transportadora {row[1]} migrada com sucesso!")
                
                except Exception as e:
                    erros += 1
                    print(f"Erro ao migrar transportadora {row[0]}: {str(e)}")
                    print(f"Dados: {row}")
                    pg_conn.rollback()
                    continue

        print("\nMigração concluída!")
        print(f"Total de transportadoras migradas: {contador}")
        print(f"Total de erros: {erros}")
        
        # Atualizar sequence
        pg_cursor.execute("""
            SELECT setval('transportadoras_id_seq', 
                         (SELECT MAX(id) FROM transportadoras));
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
    print("=== MIGRAÇÃO DE TRANSPORTADORAS ===")
    print("Início:", datetime.now())
    migrar_transportadoras()
    print("Fim:", datetime.now())
