
import psycopg2
from config import PG_CONFIG

conn = psycopg2.connect(**PG_CONFIG)
cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name LIKE 'moviment%'")
print(f"Tables: {[row[0] for row in cur.fetchall()]}")
conn.close()
