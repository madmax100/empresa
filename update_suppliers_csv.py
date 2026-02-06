
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
    input_file = r'c:\Users\Cirilo\Documents\programas\empresa\fornecedores_especificacoes_alt.csv'
    
    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        return

    print(f"Reading from {input_file}...")
    
    updated_count = 0
    errors = 0
    
    with open(input_file, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        
        for row in reader:
            try:
                # Get ID and Spec from CSV
                f_id = row.get('ID')
                spec = row.get('Especificacao')
                
                if f_id and spec:
                    # Update without fetching to optimize, but typically helpful to verify existence
                    # Using filter().update() is faster
                    count = Fornecedores.objects.filter(id=f_id).update(especificacao=spec)
                    if count > 0:
                        updated_count += count
                    else:
                        print(f"Warning: Supplier ID {f_id} not found.")
            except Exception as e:
                print(f"Error processing row {row}: {e}")
                errors += 1
                
    print(f"Update complete.")
    print(f"Total updated: {updated_count}")
    print(f"Errors: {errors}")

if __name__ == '__main__':
    run()
