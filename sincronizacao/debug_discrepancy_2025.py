
import os
import sys

# Add project root to sys.path
sys.path.append(r'c:\Users\Cirilo\Documents\programas\empresa\backend\empresa')

import django
from decimal import Decimal
from django.db.models import Sum, Q

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import ContasPagar
from contas.models.fluxo_caixa import FluxoCaixaLancamento

def check_2025_discrepancy():
    print("--- INVESTIGATION 2025 ---")
    
    # 1. Realizado logic (What 'Fluxo Realizado' page sees)
    # Filter: Paid in 2025
    realizado_qs = ContasPagar.objects.filter(
        data_pagamento__year=2025,
        status='P'
    )
    total_realizado = realizado_qs.aggregate(t=Sum('valor_pago'))['t'] or Decimal('0')
    print(f"1. REALIZADO (Paid in 2025): {total_realizado}")
    
    # 2. Previsto logic (What 'Fluxo Previsto' page sees)
    # Sync logic puts: Paid item at payment date, Open item at due date.
    
    # Let's verify what is actually IN the FluxoCaixaLancamento table for 2025
    fluxo_qs = FluxoCaixaLancamento.objects.filter(
        data__year=2025,
        tipo='saida',
        fonte_tipo='contas_pagar'
    )
    total_fluxo = fluxo_qs.aggregate(t=Sum('valor'))['t'] or Decimal('0')
    print(f"2. PREVISTO (Fluxo Table 2025): {total_fluxo}")
    
    diff = total_fluxo - total_realizado
    print(f"   DIFFERENCE (Fluxo - Realizado): {diff}")
    
    if diff != 0:
        print("\n--- ANALYZING DIFFERENCE ---")
        
        # Check for Open Bills Due in 2025 (These appear in Fluxo but NOT in Realizado)
        open_bills_2025 = ContasPagar.objects.filter(
            vencimento__year=2025,
            status='A' # Aberto
        )
        total_open = open_bills_2025.aggregate(t=Sum('valor'))['t'] or Decimal('0')
        print(f"3. OPEN BILLS DUE 2025 (Status='A'): {total_open}")
        print(f"   (These are included in Previsto but not Realizado)")
        
        remaining_diff = diff - total_open
        print(f"   REMAINING DIFF: {remaining_diff}")
        
        if abs(remaining_diff) > Decimal('0.01'):
            print("\n   Warning: Still a difference after accounting for open bills.")
            print("   Checking for value mismatches (Valor vs Valor Pago)...")
            
            # Check for items paid in 2025 where valor_pago != Fluxo val
            # (Fluxo should be using valor_pago for paid items)
            pass

if __name__ == '__main__':
    check_2025_discrepancy()
