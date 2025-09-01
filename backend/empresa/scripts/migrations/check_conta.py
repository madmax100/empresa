import pyodbc
from config import CONTAS_DB, ACCESS_PASSWORD

# Conectar ao MS Access
conn_str = f'Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={CONTAS_DB};PWD={ACCESS_PASSWORD};'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Consultar a conta específica
query = """
SELECT [CodConta a Pagar], Data, Valor, Fornecedor, 
       Vencimento, ValorTotalPago, Historico, FormaPagto,
       Condicoes, Confirmacao, Juros, Tarifas, NDuplicata,
       DataPagto, ValorPago, Local, Status, Conta
FROM Pagar 
WHERE [CodConta a Pagar] = 53674
"""

cursor.execute(query)
row = cursor.fetchone()

if row:
    print('=== CONTA 53674 NO MS ACCESS ===')
    for i, value in enumerate(row):
        field_names = [
            'CodConta a Pagar', 'Data', 'Valor', 'Fornecedor', 
            'Vencimento', 'ValorTotalPago', 'Historico', 'FormaPagto',
            'Condicoes', 'Confirmacao', 'Juros', 'Tarifas', 'NDuplicata',
            'DataPagto', 'ValorPago', 'Local', 'Status', 'Conta'
        ]
        print(f'{field_names[i]} (pos {i}): {value}')
else:
    print('Conta 53674 não encontrada')

conn.close()
