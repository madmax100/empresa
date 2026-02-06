
import psycopg2
from config import PG_CONFIG

try:
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    
    # Check current schema
    cur.execute("SELECT current_schema()")
    print(f"Current schema: {cur.fetchone()[0]}")
    
    # Check table existence in schema
    cur.execute("SELECT * FROM information_schema.tables WHERE table_name='notas_fiscais_entrada'")
    tables = cur.fetchall()
    print(f"Tables found: {tables}")
    
    # Check columns again but verbose
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'notas_fiscais_entrada'")
    columns = [row[0] for row in cur.fetchall()]
    print(f"Columns in notas_fiscais_entrada: {columns}")
    
    if 'operacao' not in columns:
        print("CRITICAL: operacao column NOT found!")
    else:
        print("operacao column found.")

    # Try simple insert (rollback after)
    print("Attempting INSERT...")
    # Using raw SQL similar to migration script
    # We need a valid ID? AutoField is ID.
    # But migration script inserts specific ID.
    sql = """
        INSERT INTO notas_fiscais_entrada (
            id, numero_nota, operacao
        ) VALUES (999999, 'TESTE', 'TEST_OP')
        ON CONFLICT (id) DO NOTHING
    """
    cur.execute(sql)
    print("INSERT affected rows:", cur.rowcount)
    
    conn.rollback()
    print("Rollback successful.")

except Exception as e:
    print(f"ERROR: {e}")
finally:
    if 'conn' in locals():
        conn.close()
