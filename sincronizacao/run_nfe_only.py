
import migrate_nfe
import psycopg2
from config import PG_CONFIG

print("Starting NFE migration standalone...")
try:
    result = migrate_nfe.migrar_nfe()
    if result:
        print("NFE Migration Success!")
    else:
        print("NFE Migration Returned False")
except Exception as e:
    print(f"Exception calling migrar_nfe: {e}")
