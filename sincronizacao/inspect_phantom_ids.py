
import os
import sys

sys.path.append(r'c:\Users\Cirilo\Documents\programas\empresa\backend\empresa')

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import ContasPagar

def check():
    ids = [54611, 54610]
    items = ContasPagar.objects.filter(id__in=ids)
    
    for item in items:
        print(f"ID: {item.id}")
        print(f"  Status: {item.status}")
        print(f"  Vencimento: {item.vencimento}")
        print(f"  Data Pagamento: {item.data_pagamento}")
        print(f"  Valor Original: {item.valor}")
        print(f"  Valor Pago: {item.valor_pago}")
        print(f"  Valor Total Pago: {item.valor_total_pago}")

if __name__ == '__main__':
    check()
