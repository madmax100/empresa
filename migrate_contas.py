import pyodbc
import psycopg2
from datetime import datetime

def clean_string(value):
    if value is None:
        return None
    return str(value).strip()

def limpar_tabelas(pg_conn):
    try:
        cursor = pg_conn.cursor()
        
        print("\nIniciando limpeza das tabelas...")
        cursor.execute("SET session_replication_role = 'replica';")
        
        tabelas = [
            'contas_bancarias'
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

def migrar_contas_bancarias():
    pg_config = {
        'dbname': 'c3mcopiasdb2',
        'user': 'cirilomax',
        'password': '226cmm100',
        'host': 'localhost',
        'port': '5432'
    }

    db_path = r"C:\Users\Cirilo\Documents\empresa\Bancos\Cadastros\Cadastros.mdb"
    
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
        
        if not limpar_tabelas(pg_conn):
            raise Exception("Falha na limpeza das tabelas. Abortando importação.")

        pg_cursor = pg_conn.cursor()
        
        # Query para buscar dados do Access
        query = """
        SELECT Codigo,
               Banco,
               NomeBanco,
               Numero,
               Agencia,
               Contato
        FROM ContasBanco
        ORDER BY Codigo
        """
        
        print("\nBuscando dados do Access...")
        access_cursor = access_conn.cursor()
        access_cursor.execute(query)

        # SQL de inserção
        insert_sql = """
            INSERT INTO contas_bancarias (
                id,
                banco,
                nome_banco,
                numero,
                agencia,
                contato
            ) VALUES (
                %s, %s, %s, %s, %s, %s
            )
        """

        # Processo de migração
        contador = 0
        erros = 0
        
        print("\nIniciando migração das contas bancárias...")
        
        rows = access_cursor.fetchall()
        for row in rows:
            try:
                dados = (
                    int(row[0]),                # id (Codigo)
                    clean_string(row[1]),       # banco
                    clean_string(row[2]),       # nome_banco
                    clean_string(row[3]),       # numero
                    clean_string(row[4]),       # agencia
                    clean_string(row[5])        # contato
                )
                
                pg_cursor.execute(insert_sql, dados)
                pg_conn.commit()
                contador += 1
                print(f"Migrada conta: {row[2]} - Ag: {row[4]} CC: {row[3]}")
                
            except Exception as e:
                erros += 1
                print(f"Erro ao migrar conta bancária {row[0]}: {str(e)}")
                print(f"Dados: {row}")
                pg_conn.rollback()
                continue

        print("\nMigração concluída!")
        print(f"Total de contas migradas: {contador}")
        print(f"Total de erros: {erros}")
        
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
    print("=== MIGRAÇÃO DE CONTAS BANCÁRIAS ===")
    print("Início:", datetime.now())
    migrar_contas_bancarias()
    print("Fim:", datetime.now())