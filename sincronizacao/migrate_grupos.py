
import pyodbc
import psycopg2
from config import PG_CONFIG, CADASTROS_DB

def clean_string(value):
    if value is None:
        return None
    return str(value).strip()

def migrar_grupos():
    print("Iniciando migração de grupos...")
    try:
        # Access connection
        conn_str = (
            r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={CADASTROS_DB};'
            'PWD=010182;'
        )
        access_conn = pyodbc.connect(conn_str)
        access_cursor = access_conn.cursor()

        # Postgres connection
        pg_conn = psycopg2.connect(**PG_CONFIG)
        pg_cursor = pg_conn.cursor()

        # Fetch from Access
        print("Lendo grupos do Access...")
        access_cursor.execute("SELECT Codigo, Descricao FROM Grupos")
        rows = access_cursor.fetchall()

        # Insert into Postgres
        insert_sql = """
            INSERT INTO grupos (id, nome)
            VALUES (%s, %s)
            ON CONFLICT (id) DO UPDATE SET
                nome = EXCLUDED.nome
        """

        count = 0
        for row in rows:
            try:
                codigo = int(row[0])
                descricao = clean_string(row[1])
                
                pg_cursor.execute(insert_sql, (codigo, descricao))
                count += 1
            except Exception as e:
                print(f"Erro ao migrar grupo {row[0]}: {e}")

        pg_conn.commit()
        print(f"Grupos migrados: {count}")

        access_conn.close()
        pg_conn.close()
        return True

    except Exception as e:
        print(f"Erro na migração de grupos: {e}")
        return False

if __name__ == "__main__":
    migrar_grupos()
