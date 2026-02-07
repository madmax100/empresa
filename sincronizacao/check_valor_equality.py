
import os
import sys

sys.path.append(r'c:\Users\Cirilo\Documents\programas\empresa\backend\empresa')

import django
from decimal import Decimal
from django.db.models import Sum, Q, F

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import ContasPagar

def check():
    # Bills Paid in 2025 with valor_pago=0
    target_bills = ContasPagar.objects.filter(
        status='P',
        data_pagamento__year=2025
    ).filter(
        Q(valor_pago__isnull=True) | Q(valor_pago=0)
    )
    
    # Check if valor (original) == valor_total_pago (actual paid)
    # We allow small diff for floating point, but essentially equality.
    
    match_count = target_bills.filter(valor=F('valor_total_pago')).count()
    total_count = target_bills.count()
    
    print(f"Total Target Bills: {total_count}")
    print(f"Bills where Original Value == Total Paid: {match_count}")
    
    diff_qs = target_bills.exclude(valor=F('valor_total_pago'))
    if diff_qs.exists():
        print(f"Bills with DIFFERENCE: {diff_qs.count()}")
        print("Sample diffs (Valor, TotalPago):", list(diff_qs.values_list('valor', 'valor_total_pago')[:3]))

if __name__ == '__main__':
    check()
