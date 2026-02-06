import os
import sys
import pyodbc
from decimal import Decimal

# Import config from sincronizacao folder
sys.path.append(os.path.join(os.path.dirname(__file__), 'sincronizacao'))
from config import EXTRATOS_DB, ACCESS_PASSWORD

def run():
    print(f"Buscando em: {EXTRATOS_DB}")
    
    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        f"DBQ={EXTRATOS_DB};"
        f"PWD={ACCESS_PASSWORD};"
    )
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    # Docs found in Postgres for 04/02: 5241, 6790
    docs = ['5241', '6790']
    
    for doc in docs:
        # Fixed query: Remove ValorTotal
        query = f"SELECT Data, Documento, Movimentacao, Quantidade, Unitario, Historico FROM NotasFiscais WHERE Documento = '{doc}'"
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            
            if not rows:
                print(f"Documento {doc}: NAO ENCONTRADO")
            else:
                for row in rows:
                    print(f"ENCONTRADO DOC {doc}:")
                    print(f"  Data: {row.Data}")
                    print(f"  Documento: {row.Documento}")
                    
                    qtd = row.Quantidade or 0
                    unit = row.Unitario or 0
                    print(f"  Total: {Decimal(str(qtd)) * Decimal(str(unit))}")
                    print(f"  Movimentacao: {row.Movimentacao}")
                    print(f"  Historico: {row.Historico}")
                    print("-" * 20)
        except Exception as e:
             print(f"Erro ao buscar {doc}: {e}")
             
    conn.close()

if __name__ == '__main__':
    run()
