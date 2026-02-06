
import psycopg2
from config import PG_CONFIG

conn = psycopg2.connect(**PG_CONFIG)
cur = conn.cursor()
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'notas_fiscais_entrada'")
columns = {row[0] for row in cur.fetchall()}
print(f"Columns: {columns}")

missing = []
for field in ['operacao', 'outras_despesas', 'outros_encargos', 'valor_icms_st', 'base_calculo_st']:
    if field not in columns:
        missing.append(field)

if missing:
    print(f"MISSING COLUMNS: {missing}")
else:
    print("All expected columns present.")
