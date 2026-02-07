
import os
import sys

sys.path.append(r'c:\Users\Cirilo\Documents\programas\empresa\backend\empresa')

import django
from decimal import Decimal
from django.db.models import Sum, Q

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import ContasPagar, ContasReceber
from contas.models.fluxo_caixa import FluxoCaixaLancamento

def check():
    start_date = '2025-01-01'
    end_date = '2025-12-31'
    
    print("--- COMPARING 2025 TOTALS ---\n")
    
    # 1. SAÍDAS (OUTFLOWS)
    print("1. SAÍDAS (OUTFLOWS)")
    
    # Realizado (Computed on fly using new logic: valor_total_pago)
    saidas_realizado = ContasPagar.objects.filter(
        status='P',
        data_pagamento__date__range=[start_date, end_date]
    ).aggregate(t=Sum('valor_total_pago'))['t'] or Decimal('0')
    
    # Previsto (From FluxoCaixaLancamento)
    saidas_previsto = FluxoCaixaLancamento.objects.filter(
        tipo='saida',
        data__range=[start_date, end_date]
    ).aggregate(t=Sum('valor'))['t'] or Decimal('0')
    
    # Open Bills (Due in 2025)
    saidas_aberto = ContasPagar.objects.filter(
        status='A',
        vencimento__date__range=[start_date, end_date]
    ).aggregate(t=Sum('valor'))['t'] or Decimal('0')
    
    print(f"  Realizado (Paid):  R$ {saidas_realizado:,.2f}")
    print(f"  Previsto (Table):  R$ {saidas_previsto:,.2f}")
    print(f"  Aberto (Open):     R$ {saidas_aberto:,.2f}")
    print(f"  Diff (Prev - Real): R$ {saidas_previsto - saidas_realizado:,.2f}")
    print(f"  Unexplained Diff:   R$ {(saidas_previsto - saidas_realizado) - saidas_aberto:,.2f}")

    print("\n--------------------------\n")

    # 2. ENTRADAS (INFLOWS)
    print("2. ENTRADAS (INFLOWS)")
    
    # Realizado (Computed on fly using valor_total_pago)
    entradas_realizado = ContasReceber.objects.filter(
        status='P',
        data_pagamento__date__range=[start_date, end_date]
    ).aggregate(t=Sum('valor_total_pago'))['t'] or Decimal('0')
    
    # Previsto (From FluxoCaixaLancamento)
    entradas_previsto = FluxoCaixaLancamento.objects.filter(
        tipo='entrada',
        data__range=[start_date, end_date]
    ).aggregate(t=Sum('valor'))['t'] or Decimal('0')
    
    # Open Receivables
    entradas_aberto = ContasReceber.objects.filter(
        status='A',
        vencimento__date__range=[start_date, end_date]
    ).aggregate(t=Sum('valor'))['t'] or Decimal('0')
    
    print(f"  Realizado (Recvd): R$ {entradas_realizado:,.2f}")
    print(f"  Previsto (Table):  R$ {entradas_previsto:,.2f}")
    print(f"  Aberto (Open):     R$ {entradas_aberto:,.2f}")
    print(f"  Diff (Prev - Real): R$ {entradas_previsto - entradas_realizado:,.2f}")
    print(f"  Unexplained Diff:   R$ {(entradas_previsto - entradas_realizado) - entradas_aberto:,.2f}")

if __name__ == '__main__':
    check()
