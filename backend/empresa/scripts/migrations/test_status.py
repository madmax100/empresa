import pyodbc
import psycopg2
from config import PG_CONFIG, CONTAS_DB, ACCESS_PASSWORD

def clean_string(value):
    """Limpa e valida strings"""
    if value is None:
        return None
    value = str(value).strip()
    return value if value else None

# Conectar aos bancos
conn_str = f'Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={CONTAS_DB};PWD={ACCESS_PASSWORD};'
access_conn = pyodbc.connect(conn_str)
pg_conn = psycopg2.connect(**PG_CONFIG)

access_cursor = access_conn.cursor()
pg_cursor = pg_conn.cursor()

# Consultar MS Access
query = """
SELECT [CodConta a Pagar], Data, Valor, Fornecedor, 
       Vencimento, ValorTotalPago, Historico, FormaPagto,
       Condicoes, Confirmacao, Juros, Tarifas, NDuplicata,
       DataPagto, ValorPago, Local, Status, Conta
FROM Pagar 
WHERE [CodConta a Pagar] = 53674
"""

access_cursor.execute(query)
row = access_cursor.fetchone()

if row:
    print("=== DADOS NO MS ACCESS ===")
    print(f"Status MS Access (pos 16): '{row[16]}'")
    
    # Aplicar lógica corrigida
    status_access = clean_string(row[16])
    status = status_access if status_access else 'A'
    
    print(f"Status limpo: '{status_access}'")
    print(f"Status final: '{status}'")
    
    # Verificar no PostgreSQL
    pg_cursor.execute("SELECT status FROM contas_pagar WHERE id = %s", (53674,))
    pg_result = pg_cursor.fetchone()
    
    if pg_result:
        print(f"\n=== DADOS NO POSTGRESQL ===")
        print(f"Status PostgreSQL atual: '{pg_result[0]}'")
    else:
        print("Conta não encontrada no PostgreSQL")

access_conn.close()
pg_conn.close()
