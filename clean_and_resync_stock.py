import os
import sys
import django
from django.db import connection

# Setup Django
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'empresa'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

# Import helper
sys.path.append(os.path.join(os.path.dirname(__file__), 'sincronizacao'))
from migrate_estoque import migrar_estoque as migrar_estoque_func

def clean_and_resync():
    print("=== LIMPEZA E RESINCRONIZAÇÃO DE ESTOQUE ===")
    
    # 1. Truncate table to remove bad records (and all others to ensure consistency)
    with connection.cursor() as cursor:
        print("Truncando tabela movimentacoes_estoque...")
        cursor.execute("TRUNCATE TABLE movimentacoes_estoque CASCADE")
    
    # 2. Run Migration
    print("Iniciando migração (com correção de datas vazias)...")
    success = migrar_estoque_func()
    
    if success:
        print("Sincronização concluída com sucesso!")
    else:
        print("Erro durante a migração.")

if __name__ == '__main__':
    clean_and_resync()
