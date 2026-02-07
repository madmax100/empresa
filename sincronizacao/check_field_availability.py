
import os
import sys

sys.path.append(r'c:\Users\Cirilo\Documents\programas\empresa\backend\empresa')

import django
from decimal import Decimal
from django.db.models import Sum, Q

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import ContasPagar

def check():
    # 1. Base set: Paid in 2025, but valor_pago is 0/Null
    paid_zero = ContasPagar.objects.filter(
        status='P',
        data_pagamento__year=2025
    ).filter(
        Q(valor_pago__isnull=True) | Q(valor_pago=0)
    )
    
    total_count = paid_zero.count()
    print(f"Total Paid-Zero Bills: {total_count}")
    
    # 2. Subset: How many of these have valor_total_pago > 0?
    has_total_pago = paid_zero.filter(valor_total_pago__gt=0).count()
    print(f"  Of which have valor_total_pago > 0: {has_total_pago}")
    
    # 3. Subset: How many have valor_total_pago == 0?
    zero_total_pago = paid_zero.filter(Q(valor_total_pago__isnull=True) | Q(valor_total_pago=0)).count()
    print(f"  Of which have valor_total_pago == 0: {zero_total_pago}")

if __name__ == '__main__':
    check()
