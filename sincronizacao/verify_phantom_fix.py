
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
    
    print("--- VERIFYING PHANTOM FIX (2025) ---\n")
    
    # 1. SAÍDAS (OUTFLOWS)
    print("1. SAÍDAS (OUTFLOWS)")
    
    # NEW Realizado Logic: 
    # - Status = P
    # - Effective Date = Coalesce(data_pagamento, vencimento) in range
    # - Value = valor_total_pago
    
    saidas_realizado = ContasPagar.objects.annotate(
        data_efetiva=Coalesce('data_pagamento', 'vencimento')
    ).filter(
        status='P',
        data_efetiva__date__range=[start_date, end_date]
    ).aggregate(t=Sum('valor_total_pago'))['t'] or Decimal('0')
    
    # Previsto (From FluxoCaixaLancamento - Unchanged reference)
    saidas_previsto = FluxoCaixaLancamento.objects.filter(
        tipo='saida',
        data__range=[start_date, end_date]
    ).aggregate(t=Sum('valor'))['t'] or Decimal('0')
    
    # Open Bills (Due in 2025)
    saidas_aberto = ContasPagar.objects.filter(
        status='A',
        vencimento__date__range=[start_date, end_date]
    ).aggregate(t=Sum('valor'))['t'] or Decimal('0')
    
    print(f"  Realizado (Fixed): R$ {saidas_realizado:,.2f}")
    print(f"  Previsto (Table):  R$ {saidas_previsto:,.2f}")
    print(f"  Aberto (Open):     R$ {saidas_aberto:,.2f}")
    
    difference = saidas_previsto - saidas_realizado
    print(f"  Diff (Prev - Real): R$ {difference:,.2f}")
    
    unexplained = difference - saidas_aberto
    print(f"  Unexplained Diff:   R$ {unexplained:,.2f}")
    
    if abs(unexplained) < 1.0:
        print("\n  SUCCESS: Difference is exactly explained by Open Bills.")
    else:
        print("\n  FAIL: Still unexplained difference.")

if __name__ == '__main__':
    check()
