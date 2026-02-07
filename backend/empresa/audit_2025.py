import os
import django
from decimal import Decimal
from datetime import date, datetime

def compare_2025():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
    django.setup()

    from contas.models.access import ContasPagar
    from contas.views.dre_views import DREView

    start_date = date(2025, 1, 1)
    end_date = date(2025, 12, 31)

    with open('audit_results_2025.txt', 'w', encoding='utf-8') as f_out:
        log = lambda s: (print(s), f_out.write(s + '\n'))
        
        log(f"--- COMPARATIVO 2025 ({start_date} a {end_date}) ---")

        from django.db.models.functions import Coalesce

        # 1. FLUXO REALIZADO (Saídas) - Exact Backend Logic
        contas_pagas_2025 = ContasPagar.objects.annotate(
            data_efetiva=Coalesce('data_pagamento', 'vencimento')
        ).filter(
            data_efetiva__date__range=[start_date, end_date],
            status='P'
        )
        
        total_fluxo_realizado = Decimal('0')
        count_fluxo = 0
        for cp in contas_pagas_2025:
            valor = cp.valor_total_pago or cp.valor or Decimal('0')
            total_fluxo_realizado += valor
            count_fluxo += 1

        # Identificar Fantasmas (P sem data_pagamento)
        fantasmas = ContasPagar.objects.annotate(
            data_efetiva=Coalesce('data_pagamento', 'vencimento')
        ).filter(
            data_efetiva__date__range=[start_date, end_date],
            status='P',
            data_pagamento__isnull=True
        )
        total_fantasmas = sum((f.valor_total_pago or f.valor or Decimal('0')) for f in fantasmas)
        
        log(f"\n[FLUXO REALIZADO (Backend Logic)]")
        log(f"Total Saídas Realizadas: R$ {total_fluxo_realizado:,.2f} ({count_fluxo} registros)")
        log(f"Destaques 'Fantasmas' (Status=P, Data=Null, usa Vencimento): R$ {total_fantasmas:,.2f} ({fantasmas.count()} registros)")


        # 2. PAINEL DE GERÊNCIA (DRE)
        dre_view = DREView()
        dre_data = dre_view._calcular_dre(start_date, end_date)

        fixos = Decimal(str(dre_data['custos_fixos']))
        variaveis_operacionais = Decimal(str(dre_data['custos_variaveis']))
        cmv = Decimal(str(dre_data['cmv']))
        
        total_gerencia_sem_cmv = fixos + variaveis_operacionais
        total_gerencia_com_cmv = fixos + variaveis_operacionais + cmv

        log(f"\n[PAINEL DE GERÊNCIA - DRE]")
        log(f"Custos Fixos:           R$ {fixos:,.2f}")
        log(f"Custos Variáveis (Op):  R$ {variaveis_operacionais:,.2f}")
        log(f"Subtotal (Fixos+Var):   R$ {total_gerencia_sem_cmv:,.2f}")
        log(f"CMV (Uso de Estoque):   R$ {cmv:,.2f}")
        log(f"Total DRE (incl. CMV):  R$ {total_gerencia_com_cmv:,.2f}")

        # 3. COMPARAÇÃO
        diff = total_fluxo_realizado - total_gerencia_sem_cmv
        log(f"\n[COMPARAÇÃO]")
        log(f"Diferença (Fluxo Realizado - DRE Fixos/Var): R$ {diff:,.2f}")
        
        if abs(diff) < 0.01:
            log(">>> RESULTADO: O total de saídas do Fluxo Realizado bate EXATAMENTE com a soma de Custos Fixos e Variáveis do DRE.")
        else:
            log(">>> RESULTADO: Há uma discrepância entre as visões.")

        # 4. MERCADORIAS
        valor_mercadoria = Decimal('0')
        for cp in contas_pagas_2025:
            espec = cp.fornecedor.especificacao if cp.fornecedor else None
            if espec and 'MERCADORIA' in espec.upper():
                valor_mercadoria += (cp.valor_total_pago or cp.valor or Decimal('0'))
                
        log(f"\n[ANÁLISE ADICIONAL]")
        log(f"Valor de 'MERCADORIA' em Contas Pagar (Fluxo): R$ {valor_mercadoria:,.2f}")
        log(f"Nota: No DRE, pagamentos de Mercadoria costumam ser substituídos pelo CMV para refletir o lucro correto.")


if __name__ == "__main__":
    compare_2025()
