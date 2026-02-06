
import psycopg2
from config import PG_CONFIG

conn = psycopg2.connect(**PG_CONFIG)
cur = conn.cursor()
tables_to_check = [
    'itens_nf_entrada', 
    'itens_nf_saida',
    'itens_contrato_locacao',
    'movimentacao_estoque',
    'saldos_estoque',
    'produtos'
]

print("Checking tables...")
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
existing_tables = {row[0] for row in cur.fetchall()}

for table in tables_to_check:
    status = "EXISTS" if table in existing_tables else "MISSING"
    print(f"{table}: {status}")

conn.close()
