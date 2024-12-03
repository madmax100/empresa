import pyodbc
import psycopg2
from datetime import datetime

def conectar_access(movimentos_path):
    """Conecta ao banco Access"""
    try:
        conn_str = (
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={movimentos_path};'
            'PWD=010182;'
        )
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"Erro ao conectar ao Access: {str(e)}")
        return None

def conectar_postgresql():
    """Conecta ao PostgreSQL"""
    try:
        pg_config = {
            'dbname': 'c3mcopiasdb',
            'user': 'cirilomax',
            'password': '226cmm100',
            'host': 'localhost',
            'port': '5432'
        }
        return psycopg2.connect(**pg_config)
    except Exception as e:
        print(f"Erro ao conectar ao PostgreSQL: {str(e)}")
        return None

def migrar_categorias(access_conn, pg_conn):
    """Migra dados da tabela Categorias"""
    try:
        # Cursor para o Access
        cursor_access = access_conn.cursor()
        cursor_access.execute("SELECT * FROM Categorias")
        
        # Cursor para o PostgreSQL
        cursor_pg = pg_conn.cursor()
        
        # Contadores
        total = 0
        migrados = 0
        
        print("\nIniciando migração de Categorias...")
        
        # Para cada registro
        for row in cursor_access.fetchall():
            total += 1
            try:
                # Insere no PostgreSQL
                cursor_pg.execute("""
                    INSERT INTO categorias (codigo, nome)
                    VALUES (%s, %s)
                    ON CONFLICT (codigo) DO UPDATE SET
                        nome = EXCLUDED.nome
                    RETURNING id;
                """, (
                    row.Codigo,
                    row.Categoria.strip() if row.Categoria else None
                ))
                
                migrados += 1
                print(f"Categoria migrada: {row.Categoria}")
                
            except Exception as e:
                print(f"Erro ao migrar categoria {row.Codigo}: {str(e)}")
                continue
        
        # Commit das alterações
        pg_conn.commit()
        
        print(f"\nMigração de Categorias concluída:")
        print(f"Total de registros: {total}")
        print(f"Registros migrados: {migrados}")
        
    except Exception as e:
        pg_conn.rollback()
        print(f"Erro durante a migração de categorias: {str(e)}")

def migrar_grupos(access_conn, pg_conn):
    """Migra dados da tabela Grupos"""
    try:
        # Cursor para o Access
        cursor_access = access_conn.cursor()
        cursor_access.execute("SELECT * FROM Grupos")
        
        # Cursor para o PostgreSQL
        cursor_pg = pg_conn.cursor()
        
        # Contadores
        total = 0
        migrados = 0
        
        print("\nIniciando migração de Grupos...")
        
        # Para cada registro
        for row in cursor_access.fetchall():
            total += 1
            try:
                # Insere no PostgreSQL
                cursor_pg.execute("""
                    INSERT INTO grupos (codigo, nome)
                    VALUES (%s, %s)
                    ON CONFLICT (codigo) DO UPDATE SET
                        nome = EXCLUDED.nome
                    RETURNING id;
                """, (
                    row.Codigo,
                    row.Descricao.strip() if row.Descricao else None
                ))
                
                migrados += 1
                print(f"Grupo migrado: {row.Descricao}")
                
            except Exception as e:
                print(f"Erro ao migrar grupo {row.Codigo}: {str(e)}")
                continue
        
        # Commit das alterações
        pg_conn.commit()
        
        print(f"\nMigração de Grupos concluída:")
        print(f"Total de registros: {total}")
        print(f"Registros migrados: {migrados}")
        
    except Exception as e:
        pg_conn.rollback()
        print(f"Erro durante a migração de grupos: {str(e)}")

def main():
    try:
        # Solicita caminho do arquivo
        movimentos_path = r"C:\Users\Cirilo\Documents\empresa\Bancos\Cadastros\Cadastros.mdb"
        
        # Conecta aos bancos
        access_conn = conectar_access(movimentos_path)
        pg_conn = conectar_postgresql()
        
        if not access_conn or not pg_conn:
            print("Erro ao conectar aos bancos de dados.")
            return
        
        # Executa as migrações
        print("\nIniciando processo de migração...")
        
        # Migra Categorias
        migrar_categorias(access_conn, pg_conn)
        
        # Migra Grupos
        migrar_grupos(access_conn, pg_conn)
        
        print("\nProcesso de migração finalizado!")
        
    except Exception as e:
        print(f"Erro durante o processo: {str(e)}")
        
    finally:
        # Fecha conexões
        if 'access_conn' in locals():
            access_conn.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == "__main__":
    main()