
import os
import django
from django.db.models import Sum, Q, Count
from django.db.models.functions import TruncMonth
from datetime import date, timedelta
from decimal import Decimal

# Configure Django standalone
import sys
sys.path.append('c:\\Users\\Cirilo\\Documents\\programas\\empresa\\backend\\empresa')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import ContasPagar, ContasReceber, NotasFiscaisSaida, NotasFiscaisEntrada, NotasFiscaisConsumo, NotasFiscaisServico

def simulate_resumo_mensal():
    data_fim = date.today()
    data_inicio = date(2023, 12, 1) # Match screenshot start roughly
    
    print(f"Simulating Resumo Mensal for: {data_inicio} to {data_fim}")

    meses_dict = {}

    # 1. Contas a Pagar (Pagos)
    pagar_mensal = ContasPagar.objects.filter(
        data_pagamento__isnull=False,
        data_pagamento__date__gte=data_inicio,
        data_pagamento__date__lte=data_fim,
        status='P'
    ).annotate(
        mes=TruncMonth('data_pagamento')
    ).select_related('fornecedor').values(
        'mes', 'valor_pago', 'fornecedor__especificacao'
    )

    for item in pagar_mensal:
        mes = item['mes']
        if mes not in meses_dict:
            meses_dict[mes] = {
                'mes': mes, 'entradas': 0, 'saidas': 0, 'entradas_contratos': 0, 'entradas_vendas': 0,
                'saidas_fixas': 0, 'saidas_variaveis': 0
            }
        
        valor = float(item['valor_pago'] or 0)
        meses_dict[mes]['saidas'] += valor
        
        esp = (item.get('fornecedor__especificacao') or '').upper()
        custos_fixos = {
            'SALARIOS', 'PRO-LABORE', 'HONOR. CONTABEIS', 'LUZ', 'AGUA', 'TELEFONE',
            'IMPOSTOS', 'ENCARGOS', 'REFEICAO', 'BENEFICIOS', 'OUTRAS DESPESAS',
            'MAT. DE ESCRITORIO', 'PAGTO SERVICOS', 'EMPRESTIMO', 'DESP. FINANCEIRAS'
        }
        if esp in custos_fixos:
            meses_dict[mes]['saidas_fixas'] += valor
        else:
            meses_dict[mes]['saidas_variaveis'] += valor

    # 2. Contas a Receber (Pagos) -> Assumir MAINLY CONTRATOS
    receber_mensal = ContasReceber.objects.filter(
        data_pagamento__isnull=False,
        data_pagamento__date__gte=data_inicio,
        data_pagamento__date__lte=data_fim,
        status='P'
    ).annotate(
        mes=TruncMonth('data_pagamento')
    ).values('mes').annotate(
        total_recebido=Sum('recebido')
    )

    for item in receber_mensal:
        mes = item['mes']
        if mes not in meses_dict:
            meses_dict[mes] = {
                'mes': mes, 'entradas': 0, 'saidas': 0, 'entradas_contratos': 0, 'entradas_vendas': 0,
                'saidas_fixas': 0, 'saidas_variaveis': 0
            }
        valor = float(item['total_recebido'] or 0)
        meses_dict[mes]['entradas'] += valor
        meses_dict[mes]['entradas_contratos'] += valor 

    # 3. NFS (Vendas)
    vendas_mensal = NotasFiscaisSaida.objects.filter(
        data__date__gte=data_inicio,
        data__date__lte=data_fim,
        operacao__istartswith='VENDA'
    ).annotate(
        mes=TruncMonth('data')
    ).values('mes').annotate(
        total=Sum('valor_total_nota')
    )

    for item in vendas_mensal:
        mes = item['mes']
        if mes not in meses_dict:
            meses_dict[mes] = {
                'mes': mes, 'entradas': 0, 'saidas': 0, 'entradas_contratos': 0, 'entradas_vendas': 0,
                'saidas_fixas': 0, 'saidas_variaveis': 0
            }
        valor = float(item['total'] or 0)
        meses_dict[mes]['entradas'] += valor
        meses_dict[mes]['entradas_vendas'] += valor

    # Output Sample
    print("\n--- Summary per Month ---")
    for mes in sorted(meses_dict.keys()):
        d = meses_dict[mes]
        print(f"Mês: {mes.strftime('%Y-%m')}")
        print(f"  Entradas Total: {d['entradas']:>12,.2f} | Contratos: {d['entradas_contratos']:>12,.2f} | Vendas: {d['entradas_vendas']:>12,.2f}")
        print(f"  Saídas Total:   {d['saidas']:>12,.2f} | Fixas:     {d['saidas_fixas']:>12,.2f} | Variáveis: {d['saidas_variaveis']:>12,.2f}")

if __name__ == "__main__":
    simulate_resumo_mensal()
