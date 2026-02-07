
import os
import sys

# Add project root to sys.path
sys.path.append(r'c:\Users\Cirilo\Documents\programas\empresa\backend\empresa')

import django
from decimal import Decimal
from django.db.models import Sum

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import ContasPagar

def check():
    open_bills = ContasPagar.objects.filter(
        vencimento__year=2025,
        status='A'
    ).aggregate(t=Sum('valor'))['t'] or Decimal('0')
    
    print(f"OPEN_BILLS_2025: {open_bills}")

if __name__ == '__main__':
    check()
