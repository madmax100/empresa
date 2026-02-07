import os
import sys
import django
from decimal import Decimal
from datetime import date, datetime

# Setup Django
sys.path.append('c:\\Users\\Cirilo\\Documents\\programas\\empresa\\backend\\empresa')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import NotasFiscaisSaida, NotasFiscaisServico

def debug_dre():
    data_inicio = date(2026, 1, 1)
    data_fim = date(2026, 1, 31)
    
    print(f"--- Faturamento DRE (NFe) para {data_inicio} a {data_fim} ---\n")
    
    # 1. NFe Vendas
    nfs = NotasFiscaisSaida.objects.filter(
        data__range=[data_inicio, data_fim],
        operacao__icontains='VENDA'
    )
    
    total_vendas = Decimal(0)
    print("--- VENDAS ---")
    for nf in nfs:
        val = nf.valor_total_nota or Decimal(0)
        total_vendas += val
        print(f"NF {nf.numero_nota} | Data: {nf.data} | Cliente: {nf.cliente} | Valor: {val}")
        
    # 2. NFS (Serviços)
    nfse = NotasFiscaisServico.objects.filter(
        data__date__gte=data_inicio,
        data__date__lte=data_fim
    )
    
    total_servicos = Decimal(0)
    print("\n--- SERVIÇOS ---")
    for nf in nfse:
        val = nf.valor_total or Decimal(0)
        total_servicos += val
        print(f"NFS {nf.numero_nota} | Data: {nf.data} | Cliente: {nf.cliente} | Valor: {val}")
        
    print(f"\nTotal Vendas: {total_vendas}")
    print(f"Total Serviços: {total_servicos}")
    print(f"TOTAL GERAL DRE: {total_vendas + total_servicos}")

if __name__ == "__main__":
    debug_dre()
