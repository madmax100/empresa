
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
    # Paid in 2025, but valor_pago is 0 or None
    paid_zero = ContasPagar.objects.filter(
        status='P',
        data_pagamento__year=2025
    ).filter(
        Q(valor_pago__isnull=True) | Q(valor_pago=0)
    )
    
    count = paid_zero.count()
    total_original = paid_zero.aggregate(t=Sum('valor'))['t'] or Decimal('0')
    
    print(f"PAID_ZERO_COUNT: {count}")
    print(f"PAID_ZERO_TOTAL_VALOR: {total_original}")
    
    if count > 0:
        print("Sample IDs:", list(paid_zero.values_list('id', flat=True)[:5]))

if __name__ == '__main__':
    check()
