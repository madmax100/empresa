
import psycopg2
from config import PG_CONFIG

conn = psycopg2.connect(**PG_CONFIG)
cur = conn.cursor()
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'grupos'")
for row in cur.fetchall():
    print(f"{row[0]}: {row[1]}")
conn.close()
