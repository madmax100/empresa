import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import ContratosLocacao, ContasReceber

print("=" * 50)
print("DIAGNÓSTICO: Entradas de Contrato")
print("=" * 50)

# 1. Total de contratos
total_contratos = ContratosLocacao.objects.count()
print(f"\n1. Total de contratos: {total_contratos}")

# 2. Contratos com cliente vinculado
contratos_com_cliente = ContratosLocacao.objects.filter(cliente__isnull=False).count()
print(f"2. Contratos com cliente vinculado: {contratos_com_cliente}")

# 3. IDs dos clientes com contrato
clientes_contrato = list(ContratosLocacao.objects.filter(cliente__isnull=False).values_list('cliente_id', flat=True)[:20])
print(f"3. Primeiros 20 IDs de clientes com contrato: {clientes_contrato}")

# 4. ContasReceber pagas
cr_pagos = ContasReceber.objects.filter(status='P', data_pagamento__isnull=False)
print(f"\n4. ContasReceber pagas: {cr_pagos.count()}")

# 5. ContasReceber pagas COM cliente
cr_com_cliente = cr_pagos.filter(cliente__isnull=False)
print(f"5. ContasReceber pagas COM cliente: {cr_com_cliente.count()}")

# 6. IDs dos clientes em ContasReceber
clientes_cr = list(cr_com_cliente.values_list('cliente_id', flat=True).distinct()[:20])
print(f"6. Primeiros 20 IDs de clientes em CR: {clientes_cr}")

# 7. Interseção - clientes que estão em ambos
clientes_contrato_set = set(ContratosLocacao.objects.filter(cliente__isnull=False).values_list('cliente_id', flat=True))
clientes_cr_set = set(cr_com_cliente.values_list('cliente_id', flat=True))
intersecao = clientes_contrato_set.intersection(clientes_cr_set)
print(f"\n7. Clientes em AMBOS (contrato + CR): {len(intersecao)}")
print(f"   IDs: {list(intersecao)[:10]}")

# 8. Valor total de entradas de clientes com contrato
from django.db.models import Sum
if intersecao:
    valor_contrato = cr_com_cliente.filter(cliente_id__in=intersecao).aggregate(total=Sum('recebido'))
    print(f"\n8. Valor total de entradas de clientes com contrato: {valor_contrato['total']}")
else:
    print("\n8. Nenhum cliente com contrato tem entradas em ContasReceber")
