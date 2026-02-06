import os
import sys
import django
import pyodbc
from decimal import Decimal
from datetime import datetime

# Setup Django
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'empresa'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
try:
    django.setup()
except:
    pass

from contas.models.access import MovimentacoesEstoque
from django.db.models import Sum, Q

# Import config from sincronizacao folder
sys.path.append(os.path.join(os.path.dirname(__file__), 'sincronizacao'))
from config import EXTRATOS_DB, ACCESS_PASSWORD

def clean_decimal(val):
    if not val: return Decimal('0.00')
    try:
        return Decimal(str(val).replace(',', '.'))
    except:
        return Decimal('0.00')

def get_access_data(start_date, end_date):
    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        f"DBQ={EXTRATOS_DB};"
        f"PWD={ACCESS_PASSWORD};"
    )
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    # Access query using correct columns based on migrate_estoque.py
    query = """
        SELECT Data, Documento, Quantidade, Unitario, Movimentacao, Produto, Historico
        FROM NotasFiscais 
        WHERE Data >= ? AND Data <= ?
        ORDER BY Data
    """
    cursor.execute(query, (start_date, end_date))
    rows = cursor.fetchall()
    
    data = []
    
    print("\n--- DADOS ORIGEM (ACCESS - Extratos.mdb) ---")
    print(f"{'Data':<12} | {'Doc':<10} | {'Tipo':<8} | {'Qtd':<8} | {'Unit':<8} | {'Total (R$)'}")
    print("-" * 75)
    
    for row in rows:
        qtd = clean_decimal(row.Quantidade)
        unit = clean_decimal(row.Unitario)
        val_total = qtd * unit
        
        mov_raw = str(row.Movimentacao).upper().strip()
        tipo = 'E' if mov_raw == 'ENTRADA' else ('S' if mov_raw == 'SAIDA' else '?')
        
        data.append({
            'data': row.Data,
            'doc': row.Documento,
            'valor': val_total,
            'tipo': tipo,
            'item': row.Produto
        })
        
        print(f"{row.Data.strftime('%Y-%m-%d'):<12} | {str(row.Documento)[:10]:<10} | {mov_raw[:8]:<8} | {qtd:<8} | {unit:<8} | {val_total}")
    
    conn.close()
    return data

def get_postgres_data(start_date, end_date):
    qs = MovimentacoesEstoque.objects.filter(
        data_movimentacao__date__range=(start_date, end_date)
    ).order_by('data_movimentacao')
    
    print("\n--- DADOS DESTINO (POSTGRESQL) ---")
    print(f"{'Data':<12} | {'Doc':<10} | {'Tipo':<5} | {'Valor (R$)'}")
    print("-" * 50)
    
    data = []
    for item in qs:
        tipo = item.tipo_movimentacao.tipo # 'E' or 'S' if loaded
        print(f"{item.data_movimentacao.strftime('%Y-%m-%d'):<12} | {str(item.documento_referencia)[:10]:<10} | {tipo:<5} | {item.valor_total}")
        data.append({
            'valor': item.valor_total,
            'tipo': tipo
        })
    return data

def run():
    start = datetime(2026, 2, 2)
    end = datetime(2026, 2, 5)
    
    print(f"Comparando período: {start.date()} a {end.date()}")
    
    try:
        access_data = get_access_data(start, end)
        pg_data = get_postgres_data(start.date(), end.date())
        
        # Calculate totals
        acc_entrada = sum(d['valor'] for d in access_data if d['tipo'] == 'E')
        acc_saida = sum(d['valor'] for d in access_data if d['tipo'] == 'S')
        
        pg_entrada = sum(d['valor'] for d in pg_data if d['tipo'] == 'E')
        pg_saida = sum(d['valor'] for d in pg_data if d['tipo'] == 'S')
        
        print("\n--- RESUMO COMPARATIVO ---")
        print(f"{'Métrica':<20} | {'Access (Origem)':<15} | {'Postgres (Destino)':<15} | {'Diferença'}")
        print("-" * 70)
        print(f"{'Qtd Registros':<20} | {len(access_data):<15} | {len(pg_data):<15} | {len(access_data) - len(pg_data)}")
        print(f"{'Total Entradas':<20} | {acc_entrada:<15} | {pg_entrada:<15} | {acc_entrada - pg_entrada}")
        print(f"{'Total Saídas':<20} | {acc_saida:<15} | {pg_saida:<15} | {acc_saida - pg_saida}")
            
    except Exception as e:
        print(f"ERRO CRITICO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run()
