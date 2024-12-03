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
        
        # Lista de tabelas que dependem de categorias
        tabelas = [
            'itens_contrato_locacao',  # Supondo que esta tabela tenha relação com categorias
            'categorias_produtos'
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

def criar_tabela_categorias(pg_cursor):
    """Cria a tabela categorias no PostgreSQL"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS categorias_produtos (
        id INTEGER PRIMARY KEY,  -- Usando Codigo como chave primária
        nome VARCHAR(50) NOT NULL,
        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ativo BOOLEAN DEFAULT true
    );

    CREATE INDEX IF NOT EXISTS idx_categorias_produtos_nome ON categorias_produtos (nome);
    """
    pg_cursor.execute(create_table_sql)

def migrar_categorias():
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
        
        # Limpar tabelas antes da importação
        if not limpar_tabelas(pg_conn):
            raise Exception("Falha na limpeza das tabelas. Abortando importação.")

        pg_cursor = pg_conn.cursor()
        
        # Criar/atualizar estrutura da tabela
        print("\nVerificando estrutura da tabela...")
        criar_tabela_categorias(pg_cursor)
        pg_conn.commit()

        # Busca dados do Access
        print("\nBuscando dados do Access...")
        access_cursor = access_conn.cursor()
        access_cursor.execute("""
            SELECT Codigo, Categoria
            FROM Categorias
            ORDER BY Codigo
        """)

        # SQL de inserção
        insert_sql = """
            INSERT INTO categorias_produtos (id, nome, data_cadastro, ativo)
            VALUES (%s, %s, %s, %s)
        """

        # Processo de migração
        contador = 0
        erros = 0
        
        print("\nIniciando migração das categorias...")
        
        while True:
            rows = access_cursor.fetchmany(1000)
            if not rows:
                break
            
            for row in rows:
                try:
                    print(f"\nProcessando categoria ID: {row[0]}")
                    
                    dados = (
                        int(row[0]),                # id (Codigo)
                        clean_string(row[1]),       # nome (Categoria)
                        datetime.now(),             # data_cadastro
                        True                        # ativo
                    )
                    
                    pg_cursor.execute(insert_sql, dados)
                    pg_conn.commit()
                    contador += 1
                    
                    print(f"Categoria {row[0]} - {row[1]} migrada com sucesso!")
                
                except Exception as e:
                    erros += 1
                    print(f"Erro ao migrar categoria {row[0]}: {str(e)}")
                    print(f"Dados que causaram erro: {row}")
                    pg_conn.rollback()
                    continue

        print("\nMigração concluída!")
        print(f"Total de categorias migradas: {contador}")
        print(f"Total de erros: {erros}")
        
        # Atualizar sequence
        pg_cursor.execute("""
            SELECT setval(pg_get_serial_sequence('categorias_produtos', 'id'), 
                         (SELECT MAX(id) FROM categorias_produtos));
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
    print("=== MIGRAÇÃO DE CATEGORIAS ===")
    print("Início:", datetime.now())
    migrar_categorias()
    print("Fim:", datetime.now())
