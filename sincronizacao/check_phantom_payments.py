
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
    # Hypothesis: Status P but no data_pagamento, falling back to 2025 vencimento.
    phantom_payments = ContasPagar.objects.filter(
        status='P',
        data_pagamento__isnull=True,
        vencimento__year=2025
    )
    
    count = phantom_payments.count()
    total = phantom_payments.aggregate(t=Sum('valor'))['t'] or Decimal('0')
    
    print(f"PHANTOM_PAYMENTS_COUNT: {count}")
    print(f"PHANTOM_PAYMENTS_TOTAL: {total}")
    
    if count > 0:
        print("Sample IDs:", list(phantom_payments.values_list('id', flat=True)[:5]))

if __name__ == '__main__':
    check()
