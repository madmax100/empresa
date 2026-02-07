import os
import sys
import django
from decimal import Decimal
from datetime import date, datetime

# Setup Django
sys.path.append('c:\\Users\\Cirilo\\Documents\\programas\\empresa\\backend\\empresa')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import ContasReceber
from django.db.models import Sum, F, DateTimeField
from django.db.models.functions import Coalesce, TruncMonth

def debug_revenue():
    data_inicio = date(2026, 1, 1)
    data_fim = date(2026, 1, 31)

    print(f"--- Debugging Revenue for {data_inicio} to {data_fim} ---\n")

    qs = ContasReceber.objects.annotate(
        data_efetiva=Coalesce('data_pagamento', 'vencimento', output_field=DateTimeField())
    ).filter(
        data_efetiva__date__gte=data_inicio,
        data_efetiva__date__lte=data_fim,
        status='P'
    )
    
    total = qs.aggregate(t=Sum('valor_total_pago'))['t']
    print(f"Total RAW Filter: {total}")
    
    print("\n--- Listing Items ---")
    items = qs.values('id', 'data_efetiva', 'valor_total_pago')
    for item in items:
        # Check if TruncMonth shifts it
        dt = item['data_efetiva'] # This is datetime
        print(f"ID: {item['id']} | Date: {dt} | Val: {item['valor_total_pago']}")

    # Check TruncMonth aggregation
    print("\n--- TruncMonth Aggregation ---")
    agg = qs.annotate(mes=TruncMonth('data_efetiva')).values('mes').annotate(t=Sum('valor_total_pago'))
    for row in agg:
        print(f"Month: {row['mes']} | Total: {row['t']}")

if __name__ == "__main__":
    debug_revenue()
