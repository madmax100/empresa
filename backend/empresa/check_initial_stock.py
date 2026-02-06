
import os
import sys
import django
from django.db.models import Sum

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import EstoqueInicial



from contas.models.access import Produtos
from django.db.models import Sum

def check_stock():
    print("--- CHECKING PRODUCT STOCK ---")
    total_products = Produtos.objects.count()
    # Filter products that have non-zero stock
    products_with_stock = Produtos.objects.filter(estoque_atual__gt=0).count()
    
    # Calculate total quantity
    total_stock_qty = Produtos.objects.aggregate(Sum('estoque_atual'))
    
    print(f"Total Products: {total_products}")
    print(f"Products with Stock > 0: {products_with_stock}")
    print(f"Total Stock Quantity (Sum): {total_stock_qty['estoque_atual__sum']}")
    print("------------------------------")

if __name__ == "__main__":
    check_stock()



if __name__ == "__main__":
    check_stock()
