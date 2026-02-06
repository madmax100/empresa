
import os
import django
from datetime import date, timedelta
from django.conf import settings
from django.db.models import Sum, Q

# Configure Django standalone
import sys
sys.path.append('c:\\Users\\Cirilo\\Documents\\programas\\empresa\\backend\\empresa')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import ContasPagar, ContasReceber, NotasFiscaisSaida, NotasFiscaisEntrada, NotasFiscaisConsumo, NotasFiscaisServico

def verify_fluxo():
    # Define period (last 30 days)
    data_fim = date.today()
    data_inicio = data_fim - timedelta(days=30)
    
    print(f"Verifying Cash Flow for period: {data_inicio} to {data_fim}")

    # 1. Contas Receber (Realizado)
    cr = ContasReceber.objects.filter(
        data_pagamento__isnull=False,
        data_pagamento__date__gte=data_inicio,
        data_pagamento__date__lte=data_fim,
        status='P'
    ).aggregate(total=Sum('recebido'))
    total_cr = float(cr['total'] or 0)
    print(f"Contas Receber Realizadas: R$ {total_cr:.2f}")

    # 2. NFS (Vendas a Vista) - With Exclusion Filters
    nfs = NotasFiscaisSaida.objects.filter(
        data__date__gte=data_inicio,
        data__date__lte=data_fim,
        condicoes__icontains='vista'
    ).exclude(
        Q(operacao__icontains='REMESSA') |
        Q(operacao__icontains='RETORNO') |
        Q(operacao__icontains='DEVOLUCAO') |
        Q(operacao__icontains='REQUISICAO') |
        Q(operacao__icontains='OUTRAS') |
        Q(cfop__startswith='5.9') |
        Q(cfop__startswith='6.9') |
        Q(cfop__icontains='REQ')
    ).aggregate(total=Sum('valor_total_nota'))
    total_nfs = float(nfs['total'] or 0)
    print(f"NFS A Vista (Valid): R$ {total_nfs:.2f}")

    # 3. NFServ (Servicos a Vista)
    nfserv = NotasFiscaisServico.objects.filter(
        data__date__gte=data_inicio,
        data__date__lte=data_fim,
        condicoes__icontains='vista'
    ).aggregate(total=Sum('valor_total'))
    total_nfserv = float(nfserv['total'] or 0)
    print(f"NFServ A Vista: R$ {total_nfserv:.2f}")

    print("-" * 30)
    print(f"TOTAL ENTRADAS: R$ {total_cr + total_nfs + total_nfserv:.2f}")
    if total_nfs > 0:
        print("SUCCESS: NFS data is now contributing to cash flow!")
    else:
        print("WARNING: No NFS data found (might be no sales in period).")

if __name__ == "__main__":
    verify_fluxo()
