import os
import django
from django.db.models import Q

# Configurar o ambiente do Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "empresa.settings")
django.setup()

from contas.models import ContratosLocacao

# Função para verificar se um valor é um número válido
def is_number(value):
    if value is None or value == "":
        return False
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

# Buscar os contratos com valorpacela inválido, vazio ou nulo
contratos_invalidos = ContratosLocacao.objects.exclude(
    valorpacela__regex=r'^\d+(\.\d+)?$'
)

# Deletar os contratos inválidos
count = contratos_invalidos.count()
contratos_invalidos.delete()

print(f"{count} contratos inválidos foram deletados.")