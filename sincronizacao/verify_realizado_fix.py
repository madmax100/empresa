
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
    # Simulate Fluxo Realizado 2025 logic with NEW field (valor_total_pago)
    start_date = '2025-01-01'
    end_date = '2025-12-31'
    
    filters_cp = {
        'data_pagamento__isnull': False,
        'data_pagamento__date__gte': start_date,
        'data_pagamento__date__lte': end_date,
        'status': 'P'
    }
    
    qs = ContasPagar.objects.filter(**filters_cp)
    
    # New logic: sum of valor_total_pago
    total_realizado = qs.aggregate(t=Sum('valor_total_pago'))['t'] or Decimal('0')
    
    print(f"NEW REALIZADO 2025 (using valor_total_pago): {total_realizado}")
    
    # Compare with Open Bills logic found earlier
    # Realizado + Open Bills should approx equal Previsto
    # We recall Previsto (old) was ~841k
    # Open Bills 2025 was ~708
    
    print("Expected: Should clearly exceed the old 774k value.")

if __name__ == '__main__':
    check()
