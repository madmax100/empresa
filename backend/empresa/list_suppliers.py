
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import Fornecedores

suppliers = Fornecedores.objects.all().values_list('nome', flat=True)[:100]
for name in suppliers:
    print(name)
