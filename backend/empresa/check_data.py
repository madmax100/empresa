
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import Fornecedores

print(f'Fornecedores count: {Fornecedores.objects.count()}')

print('\n--- Especificacao Stats ---')
specs = Fornecedores.objects.exclude(especificacao__isnull=True).exclude(especificacao='').values_list('especificacao', flat=True).distinct()
print(f'Distinct specs: {list(specs)}')

print('\n--- Tipo Stats ---')
tipos = Fornecedores.objects.exclude(tipo__isnull=True).exclude(tipo='').values_list('tipo', flat=True).distinct()
print(f'Distinct tipos: {list(tipos)[:20]}')

print('\n--- Sample Suppliers (first 10) ---')
suppliers = Fornecedores.objects.all().values('nome', 'especificacao', 'tipo')[:10]
for s in suppliers:
    print(f"Nome: {s['nome']}, Espec: '{s['especificacao']}', Tipo: '{s['tipo']}'")
