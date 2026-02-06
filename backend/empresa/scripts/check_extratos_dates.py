
import pyodbc
import os
from datetime import datetime

files = [
    r"C:\Users\Cirilo\Documents\programas\empresa\InterMax.03.02.2026\Bancos\Extratos\Extratos.mdb",
    r"C:\Users\Cirilo\Documents\programas\empresa\InterMax.03.02.2026\Dados\Extratos\Extratos.mdb",
    r"C:\Users\Cirilo\Documents\programas\empresa\InterMax.03.02.2026\Dados Limpos\Extratos\Extratos.mdb"
]

print(f"{'FILE':<80} | {'MAX DATE':<20} | {'COUNT':<10}")
print("-" * 115)

for db_path in files:
    if not os.path.exists(db_path):
        print(f"{db_path:<80} | {'NOT FOUND':<20} | {'-'}")
        continue
        
    try:
        conn_str = f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};PWD=010182'
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Check if table exists
        tables = [t.table_name for t in cursor.tables(tableType='TABLE')]
        if 'NotasFiscais' not in tables:
             print(f"{db_path:<80} | {'NO TABLE':<20} | {'-'}")
             conn.close()
             continue
             
        # Get Max Date and Count
        cursor.execute("SELECT MAX(Data), COUNT(*) FROM NotasFiscais")
        row = cursor.fetchone()
        max_date = row[0]
        count = row[1]
        
        result = f"{db_path:<80} | {str(max_date):<20} | {count:<10}\n"
        print(result)
        with open('extratos_check_result.txt', 'a', encoding='utf-8') as f:
            f.write(result)
        conn.close()
        
    except Exception as e:
        error_msg = f"{db_path:<80} | {'ERROR':<20} | {str(e)}\n"
        print(error_msg)
        with open('extratos_check_result.txt', 'a', encoding='utf-8') as f:
            f.write(error_msg)
