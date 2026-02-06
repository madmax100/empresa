
import psycopg2
from config import PG_CONFIG

def check_types():
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()

        cur.execute("""
            SELECT DISTINCT operacao, cfop
            FROM notas_fiscais_saida
            WHERE condicoes ILIKE '%VISTA%'
        """)
        
        print("Distinct Types for 'A VISTA' NFS:")
        for row in cur.fetchall():
            print(f"Operacao: {repr(row[0])} | CFOP: {repr(row[1])}")

        conn.close()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_types()
