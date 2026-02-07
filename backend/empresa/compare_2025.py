import os
import django
from decimal import Decimal
from datetime import date
from django.conf import settings

# Setup Django manually
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
try:
    django.setup()
except Exception:
    pass

from contas.views.dre_views import DREView
from contas.views.fluxo_caixa_realizado import FluxoCaixaRealizadoViewSet

def compare_2025():
    output = []
    
    start_date = date(2025, 1, 1)
    end_date = date(2025, 12, 31)
    
    # 1. DRE
    dre_view = DREView()
    dre_view.PERCENTUAL_IMPOSTOS = Decimal(0)
    dre_data = dre_view._calcular_dre(start_date, end_date)
    
    # 2. Resumo Mensal
    viewset = FluxoCaixaRealizadoViewSet()
    class MockRequest:
        def __init__(self, query_params):
            self.query_params = query_params
    
    request = MockRequest({
        'data_inicio': str(start_date),
        'data_fim': str(end_date)
    })
    
    response = viewset.resumo_mensal(request)
    if response.status_code != 200:
        output.append(f"Erro ao calcular Resumo Mensal: {response.status_code}")
        return

    totais = response.data['totais']
    resumo_receita = Decimal(str(totais['total_entradas']))
    resumo_saidas = Decimal(str(totais['total_saidas']))
    resumo_resultado = Decimal(str(totais['saldo_liquido']))

    resumo_fixas = Decimal(str(totais.get('saidas_fixas', 0)))
    resumo_variaveis = Decimal(str(totais.get('saidas_variaveis', 0))) # Inclui CMV
    resumo_cmv = Decimal(str(totais.get('cmv', 0)))
    resumo_variaveis_only = Decimal(str(totais.get('custos_variaveis', 0)))
    
    dre_fixas = Decimal(str(dre_data.get('custos_fixos', 0)))
    dre_variaveis = Decimal(str(dre_data.get('custos_variaveis', 0)))
    dre_cmv = Decimal(str(dre_data.get('cmv', 0)))
    dre_total_variaveis = dre_variaveis + dre_cmv
    
    try:
        if not isinstance(dre_data, dict):
            output.append(f"ERRO: dre_data não é um dicionário. Tipo: {type(dre_data)}")
            output.append(f"Conteúdo: {dre_data}")
            raise ValueError("Dados DRE inválidos")
            
        output.append(f"Chaves no dre_data: {list(dre_data.keys())}")
        
        val_faturamento = dre_data.get('faturamento_bruto', 0)
        val_op = dre_data.get('despesas_operacionais', 0)
        val_cmv = dre_data.get('cmv', 0)
        val_res = dre_data.get('resultado_liquido', 0)
        
        dre_receita = Decimal(str(val_faturamento))
        dre_saidas = Decimal(str(val_op)) + Decimal(str(val_cmv))
        dre_resultado = Decimal(str(val_res))
    except Exception as e:
        output.append(f"ERRO ao processar dados do DRE: {e}")
        import traceback
        output.append(traceback.format_exc())
        with open('comparison_2025.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(output))
        print('\n'.join(output))
        return
    
    output.append(f"--- Comparação Anual 2025: Visão Geral (DRE) vs Resumo Mensal ---\n")
    output.append(f"[DRE 2025]")
    output.append(f"  Receita:    {dre_receita}")
    output.append(f"  Saídas:     {dre_saidas}")
    output.append(f"    - Fixas:     {dre_fixas}")
    output.append(f"    - Variáveis: {dre_total_variaveis} (Var: {dre_variaveis} + CMV: {dre_cmv})")
    output.append(f"  Resultado:  {dre_resultado}")
    
    output.append(f"\n[Resumo Mensal 2025]")
    output.append(f"  Receita:    {resumo_receita}")
    output.append(f"  Saídas:     {resumo_saidas}")
    output.append(f"    - Fixas:     {resumo_fixas}")
    output.append(f"    - Variáveis: {resumo_variaveis} (Var: {resumo_variaveis_only} + CMV: {resumo_cmv})")
    output.append(f"  Resultado:  {resumo_resultado}")
    
    output.append(f"\n[Diferenças]")
    output.append(f"  Receita:    {dre_receita - resumo_receita}")
    output.append(f"  Saídas:     {dre_saidas - resumo_saidas}")
    output.append(f"    - Fixas:     {dre_fixas - resumo_fixas}")
    output.append(f"    - Variáveis Total: {dre_total_variaveis - resumo_variaveis}")
    output.append(f"      - Custos Var:    {dre_variaveis - resumo_variaveis_only}")
    output.append(f"      - CMV:           {dre_cmv - resumo_cmv}")
    output.append(f"  Resultado:  {dre_resultado - resumo_resultado}")
    
    if (dre_receita - resumo_receita) == 0 and abs(dre_resultado - resumo_resultado) < 0.1:
        output.append("\n✅ RESULTADO: Compatibilidade Total!")
    else:
        output.append("\n⚠️ RESULTADO: Divergência encontrada (Verificar detalhes)")
        
    with open('comparison_2025.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))
    
    print('\n'.join(output))

if __name__ == "__main__":
    compare_2025()
