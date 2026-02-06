
import psycopg2
from config import PG_CONFIG

try:
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    
    tables = [
        'notas_fiscais_entrada',
        'notas_fiscais_saida',
        'notas_fiscais_servico', 
        'notas_fiscais_consumo',
        'clientes',
        'fornecedores',
        'produtos',
        'grupos',
        'itens_nf_entrada',
        'itens_nf_saida',
        'itens_nf_servico'
    ]
    
    print("=== Row Counts ===")
    for table in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"{table}: {count}")
        except Exception as e:
            print(f"{table}: ERROR - {e}")
            conn.rollback() # Need rollback to proceed after error
            
    conn.close()

except Exception as e:
    print(f"Connection failed: {e}")
