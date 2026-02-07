
import os
import sys

sys.path.append(r'c:\Users\Cirilo\Documents\programas\empresa\backend\empresa')

import django
from decimal import Decimal
from django.db.models import Sum, Q, F
from django.db.models.functions import Coalesce

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import ContasPagar, ContasReceber
from contas.models.fluxo_caixa import FluxoCaixaLancamento

def check():
    start_date = '2025-01-01'
    end_date = '2025-12-31'
    
    print("--- VERIFYING FINAL FIX (2025) ---\n")
    
    # 1. SAÍDAS (OUTFLOWS)
    print("1. SAÍDAS (OUTFLOWS)")
    
    # NEW Realizado Logic V2: 
    # - Status = P
    # - Effective Date = Coalesce(data_pagamento, vencimento) in range
    # - Value Logic: In Python, we sum(valor_total_pago or valor)
    #   We can't easily express "or valor" in aggregate without Case/When
    #   So we fetch and sum in Python to match the View exactly.
    
    qs_pagar = ContasPagar.objects.annotate(
        data_efetiva=Coalesce('data_pagamento', 'vencimento'),
    ).filter(
        status='P',
        data_efetiva__date__range=[start_date, end_date]
    )
    
    saidas_realizado = Decimal('0')
    for c in qs_pagar:
        val = c.valor_total_pago or c.valor or Decimal('0')
        saidas_realizado += val
    
    # Previsto
    saidas_previsto = FluxoCaixaLancamento.objects.filter(
        tipo='saida',
        data__range=[start_date, end_date]
    ).aggregate(t=Sum('valor'))['t'] or Decimal('0')
    
    # Open Bills
    saidas_aberto = ContasPagar.objects.filter(
        status='A',
        vencimento__date__range=[start_date, end_date]
    ).aggregate(t=Sum('valor'))['t'] or Decimal('0')
    
    print(f"  Realizado (Fixed V2): R$ {saidas_realizado:,.2f}")
    print(f"  Previsto (Table):     R$ {saidas_previsto:,.2f}")
    print(f"  Aberto (Open):        R$ {saidas_aberto:,.2f}")
    
    difference = saidas_previsto - saidas_realizado
    print(f"  Diff (Prev - Real):   R$ {difference:,.2f}")
    
    unexplained = difference - saidas_aberto
    print(f"  Unexplained Diff:     R$ {unexplained:,.2f}")
    
    if abs(unexplained) < 1.0:
        print("\n  SUCCESS: Difference is exactly explained by Open Bills!")
    else:
        print("\n  FAIL: Still unexplained difference.")

if __name__ == '__main__':
    check()
