
import os
import django

# Configure Django standalone
import sys
sys.path.append('c:\\Users\\Cirilo\\Documents\\programas\\empresa\\backend\\empresa')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import NotasFiscaisSaida

def list_operations():
    ops = NotasFiscaisSaida.objects.values_list('operacao', flat=True).distinct().order_by('operacao')
    
    print("Distinct Operations in NotasFiscaisSaida:")
    for op in ops:
        if op:
            print(f"- {op}")

if __name__ == "__main__":
    list_operations()
