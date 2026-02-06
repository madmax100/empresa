
import pyodbc
from config import CADASTROS_DB

conn_str = (
    r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'
    f'DBQ={CADASTROS_DB};'
    'PWD=010182;'
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()
for row in cursor.columns(table='Grupos'):
    print(row.column_name)
conn.close()
