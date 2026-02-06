
import os
import django
import sys
import csv

# Setup Django environment
sys.path.append(r'c:\Users\Cirilo\Documents\programas\empresa\backend\empresa')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import Fornecedores

def run():
    output_file = 'fornecedores_especificacoes.csv'
    
    # Query all suppliers
    suppliers = Fornecedores.objects.all().order_by('nome')
    
    print(f"Exporting {suppliers.count()} suppliers to {output_file}...")
    
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        # Header
        writer.writerow(['ID', 'Fornecedor', 'Especificacao'])
        
        for s in suppliers:
            writer.writerow([
                s.id,
                s.nome,
                s.especificacao or ''
            ])
            
    print(f"Export complete: {os.path.abspath(output_file)}")

if __name__ == '__main__':
    run()
