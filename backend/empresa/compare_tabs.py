import os
import sys
import django
from decimal import Decimal
from datetime import date, datetime

# Setup Django
sys.path.append('c:\\Users\\Cirilo\\Documents\\programas\\empresa\\backend\\empresa')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.views.dre_views import DREView
from contas.models.access import ContasPagar, ContasReceber, ContratosLocacao
from django.db.models import Sum, Case, When, Value, DecimalField, F, DateTimeField
from django.db.models.functions import Coalesce, TruncMonth

def compare_values():
    # Define period: January 2026
    data_inicio = date(2026, 1, 1)
    data_fim = date(2026, 1, 31)
    
    # Disable Estimated Taxes
    DREView.PERCENTUAL_IMPOSTOS = Decimal(0)
    
    print(f"--- Comparando Período: {data_inicio} a {data_fim} (Sem Impostos Estimados) ---\n")

    # 1. Visão Geral (DRE)
    print("Calculando DRE (Visão Geral)...")
    dre_view = DREView()
    try:
        dre_data = dre_view._calcular_dre(data_inicio, data_fim)
        # dre_data return depends on signature. The code I read passes it to a dict construction.
        # It returns: faturamento_bruto, faturamento_vendas, ..., resultado_liquido, ...
        # Based on lines 302+:
        # It seems _calcular_dre returns a dictionary? No, wait.
        # Line 184: dre = self._calcular_dre(...)
        # Line 197: 'dre': dre
        # Let's check _calcular_dre definition again. 
        # It ends at line 332 returning a DICT.
        
        dre_receita = dre_data['faturamento_bruto']
        dre_despesa = dre_data['despesas_operacionais'] # + impostos + cmv?
        # Lucro Liquido = Faturamento - Impostos - CMV - Despesas
        # The user likely sees "Receitas", "Despesas", "Resultado".
        # In DRE: 
        # Receita = Faturamento Bruto
        # Despesas Total = Impostos + CMV + Despesas Operacionais ?
        # Or Despesas = Despesas Operacionais only?
        # Visão Geral usually shows: Faturamento, Impostos, CMV, Despesas, Resultado.
        
        dre_resultado = dre_data['resultado_liquido']
        dre_impostos = dre_data['impostos_vendas']
        dre_cmv = dre_data['cmv']
        dre_despesas_ops = dre_data['despesas_operacionais']
        
        dre_total_deducoes = dre_impostos + dre_cmv + dre_despesas_ops

    except Exception as e:
        print(f"Erro ao calcular DRE: {e}")
        import traceback
        traceback.print_exc()
        return

    # 2. Resumo Mensal (Fluxo de Caixa)
    print("Calculando Fluxo de Caixa (Resumo Mensal)...")
    # Copied logic from FluxoCaixaRealizadoViewSet.resumo_mensal
    
    # Receitas
    clientes_com_contrato = list(
        ContratosLocacao.objects.filter(cliente__isnull=False).values_list('cliente_id', flat=True).distinct()
    )
    
    receber_total = ContasReceber.objects.annotate(
        data_efetiva=Coalesce('data_pagamento', 'vencimento', output_field=DateTimeField())
    ).filter(
        data_efetiva__date__gte=data_inicio,
        data_efetiva__date__lte=data_fim,
        status='P'
    ).aggregate(
        total=Sum('valor_total_pago')
    )['total'] or Decimal(0)

    # Despesas
    pagar_total = ContasPagar.objects.annotate(
        data_efetiva=Coalesce('data_pagamento', 'vencimento', output_field=DateTimeField())
    ).filter(
        data_efetiva__date__gte=data_inicio,
        data_efetiva__date__lte=data_fim,
        status='P'
    ).aggregate(
        total=Sum('valor_total_pago')
    )['total'] or Decimal(0)
    
    fluxo_receita = float(receber_total)
    fluxo_despesa = float(pagar_total)
    fluxo_resultado = fluxo_receita - fluxo_despesa

    # 3. Comparison Output
    print("\n--- RESULTADOS ---")
    print(f"{'Item':<20} | {'Visão Geral (DRE)':<20} | {'Resumo Mensal (Caixa)':<20} | {'Diferença':<15}")
    print("-" * 85)
    
    diff_receita = dre_receita - fluxo_receita
    print(f"{'Receitas':<20} | {dre_receita:,.2f}             | {fluxo_receita:,.2f}             | {diff_receita:,.2f}")
    
    # Note: DRE Deductions include Impostos and CMV which are NOT in Accounts Payable usually (unless explicit)
    # But User probably compares "Total Outflows" vs "Total Expenses + Costs"
    print(f"{'Despesas (Total)':<20} | {dre_total_deducoes:,.2f}             | {fluxo_despesa:,.2f}             | {dre_total_deducoes - fluxo_despesa:,.2f}")
    
    diff_result = dre_resultado - fluxo_resultado
    print(f"{'Resultado':<20} | {dre_resultado:,.2f}             | {fluxo_resultado:,.2f}             | {diff_result:,.2f}")

    print("\n--- DETALHAMENTO DRE ---")
    print(f"Faturamento: {dre_receita:,.2f}")
    print(f"(-) Impostos: {dre_impostos:,.2f}")
    print(f"(-) CMV: {dre_cmv:,.2f}")
    print(f"(-) Desp. Op: {dre_despesas_ops:,.2f}")
    print(f"(=) Resultado: {dre_resultado:,.2f}")

if __name__ == "__main__":
    compare_values()
