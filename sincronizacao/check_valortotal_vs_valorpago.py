
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
    # Check bills paid in 2025 where valor_pago is 0 but valor_total_pago > 0
    mismatch_qs = ContasPagar.objects.filter(
        status='P',
        data_pagamento__year=2025,
        valor_pago=0,
        valor_total_pago__gt=0
    )
    
    count = mismatch_qs.count()
    total_vp = mismatch_qs.aggregate(t=Sum('valor_pago'))['t'] or Decimal('0')
    total_vtp = mismatch_qs.aggregate(t=Sum('valor_total_pago'))['t'] or Decimal('0')
    
    print(f"COUNT (ValorPago=0, ValorTotalPago>0): {count}")
    print(f"SUM ValorPago: {total_vp}")
    print(f"SUM ValorTotalPago: {total_vtp}")
    
    if count > 0:
        print("Sample IDs:", list(mismatch_qs.values_list('id', flat=True)[:5]))

if __name__ == '__main__':
    check()
