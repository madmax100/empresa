
import os
import django

import sys
sys.path.append('c:\\Users\\Cirilo\\Documents\\programas\\empresa\\backend\\empresa')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import NotasFiscaisSaida

def list_conditions():
    conds = NotasFiscaisSaida.objects.values_list('condicoes', flat=True).distinct().order_by('condicoes')
    
    print("Distinct Conditions in NotasFiscaisSaida:")
    for c in conds:
        if c:
            print(f"- {c}")

if __name__ == "__main__":
    list_conditions()
