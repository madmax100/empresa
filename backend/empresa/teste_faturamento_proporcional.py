#!/usr/bin/env python3
"""
Teste para verificar se o endpoint está calculando
corretamente o faturamento proporcional ao período
"""

import os
import sys
import django
import requests
from datetime import datetime, date

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

def teste_faturamento_proporcional():
    """
    Testa diferentes períodos para verificar o cálculo proporcional
    """
    print("=" * 80)
    print("📊 TESTE DE FATURAMENTO PROPORCIONAL")
    print("=" * 80)
    
    # Casos de teste com diferentes períodos
    casos_teste = [
        {
            'nome': 'Período de 15 dias (metade do mês)',
            'data_inicial': '2025-08-01',
            'data_final': '2025-08-15'
        },
        {
            'nome': 'Período de 10 dias (1/3 do mês)', 
            'data_inicial': '2025-08-01',
            'data_final': '2025-08-10'
        },
        {
            'nome': 'Período de 30 dias (mês completo)',
            'data_inicial': '2025-08-01', 
            'data_final': '2025-08-30'
        },
        {
            'nome': 'Período de 7 dias (semana)',
            'data_inicial': '2025-08-01',
            'data_final': '2025-08-07'
        }
    ]
    
    url = "http://localhost:8000/api/contratos_locacao/suprimentos/"
    
    for i, caso in enumerate(casos_teste, 1):
        print(f"\n{i}. {caso['nome']}")
        print("=" * 60)
        
        params = {
            'data_inicial': caso['data_inicial'],
            'data_final': caso['data_final']
        }
        
        # Calcular dias manualmente para comparação
        data_inicio = datetime.strptime(caso['data_inicial'], '%Y-%m-%d').date()
        data_fim = datetime.strptime(caso['data_final'], '%Y-%m-%d').date()
        dias_periodo = (data_fim - data_inicio).days + 1
        
        print(f"📅 Período: {caso['data_inicial']} a {caso['data_final']}")
        print(f"📊 Dias no período: {dias_periodo}")
        
        try:
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verificar resumo financeiro
                resumo_financeiro = data.get('resumo_financeiro', {})
                faturamento_total = resumo_financeiro.get('faturamento_total_proporcional', 0)
                metodo_calculo = resumo_financeiro.get('metodo_calculo', 'N/A')
                
                print(f"💰 Faturamento total proporcional: R$ {faturamento_total:,.2f}")
                print(f"🔧 Método de cálculo: {metodo_calculo}")
                
                # Analisar alguns contratos específicos
                resultados = data.get('resultados', [])
                print(f"\n🔍 Análise de contratos (primeiros 3):")
                
                for j, resultado in enumerate(resultados[:3], 1):
                    contrato_id = resultado.get('contrato_id')
                    valores = resultado.get('valores_contratuais', {})
                    vigencia = resultado.get('vigencia', {})
                    analise = resultado.get('analise_financeira', {})
                    
                    valor_mensal = valores.get('valor_mensal', 0)
                    faturamento_prop = valores.get('faturamento_proporcional', 0)
                    calculo = valores.get('calculo', 'N/A')
                    
                    periodo_efetivo = vigencia.get('periodo_efetivo', {})
                    dias_vigentes = periodo_efetivo.get('dias_vigentes', 0)
                    
                    # Verificar cálculo manual
                    faturamento_esperado = (valor_mensal * dias_vigentes) / 30
                    diferenca = abs(faturamento_prop - faturamento_esperado)
                    
                    print(f"\n   Contrato {contrato_id}:")
                    print(f"      💰 Valor mensal: R$ {valor_mensal:.2f}")
                    print(f"      📅 Dias vigentes: {dias_vigentes}")
                    print(f"      💵 Faturamento proporcional: R$ {faturamento_prop:.2f}")
                    print(f"      🧮 Cálculo: {calculo}")
                    print(f"      ✓ Verificação: R$ {faturamento_esperado:.2f} (dif: R$ {diferenca:.2f})")
                    
                    if diferenca < 0.01:
                        print(f"      ✅ Cálculo correto!")
                    else:
                        print(f"      ❌ Diferença detectada!")
                
                # Verificar proporcionalidade
                if i == 1:  # Guardar referência do primeiro caso para comparar
                    faturamento_referencia = faturamento_total
                    dias_referencia = dias_periodo
                else:
                    # Calcular proporção esperada
                    proporcao_esperada = dias_periodo / dias_referencia
                    faturamento_esperado = faturamento_referencia * proporcao_esperada
                    
                    print(f"\n📈 Verificação de proporcionalidade:")
                    print(f"   Proporção de dias: {dias_periodo}/{dias_referencia} = {proporcao_esperada:.2f}")
                    print(f"   Faturamento esperado: R$ {faturamento_esperado:,.2f}")
                    print(f"   Faturamento real: R$ {faturamento_total:,.2f}")
                    
                    diferenca_prop = abs(faturamento_total - faturamento_esperado)
                    if diferenca_prop < 1.0:  # Tolerância de R$ 1,00
                        print(f"   ✅ Proporcionalidade correta!")
                    else:
                        print(f"   ⚠️ Diferença: R$ {diferenca_prop:.2f}")
                
            else:
                print(f"❌ Erro na requisição: Status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Erro: Servidor não está rodando")
            break
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
    
    print(f"\n" + "=" * 80)
    print("✅ TESTE DE FATURAMENTO PROPORCIONAL CONCLUÍDO")
    print("=" * 80)

if __name__ == "__main__":
    teste_faturamento_proporcional()
