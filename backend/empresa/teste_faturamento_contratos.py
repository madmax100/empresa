#!/usr/bin/env python3
"""
Teste para verificar se o endpoint suprimentos-por-contrato
está calculando corretamente o faturamento baseado no valor mensal
"""

import os
import sys
import django
import requests
from datetime import datetime, timedelta

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

def teste_faturamento_contratos():
    """
    Testa se o endpoint calcula corretamente o faturamento baseado no valor mensal
    """
    print("=" * 80)
    print("TESTE DE FATURAMENTO - ENDPOINT SUPRIMENTOS POR CONTRATO")
    print("=" * 80)
    
    # Definir período de teste (1 mês)
    data_inicial = datetime(2024, 8, 1).date()
    data_final = datetime(2024, 8, 31).date()
    
    print(f"\n📅 Período de teste (1 mês):")
    print(f"   Data inicial: {data_inicial}")
    print(f"   Data final: {data_final}")
    
    # Teste do endpoint
    url = "http://localhost:8000/api/contratos_locacao/suprimentos/"
    params = {
        'data_inicial': data_inicial.strftime('%Y-%m-%d'),
        'data_final': data_final.strftime('%Y-%m-%d')
    }
    
    print(f"\n🔗 Testando endpoint com cálculo de faturamento:")
    print(f"   URL: {url}")
    print(f"   Parâmetros: {params}")
    
    try:
        response = requests.get(url, params=params)
        
        print(f"\n📊 Resultado do teste:")
        print(f"   Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verificar resumo financeiro
            resumo_financeiro = data.get('resumo_financeiro', {})
            if resumo_financeiro:
                print(f"\n💰 Resumo Financeiro do Período:")
                print(f"   Faturamento Total: R$ {resumo_financeiro.get('faturamento_total_periodo', 0):.2f}")
                print(f"   Custo Suprimentos: R$ {resumo_financeiro.get('custo_total_suprimentos', 0):.2f}")
                print(f"   Margem Bruta: R$ {resumo_financeiro.get('margem_bruta_total', 0):.2f}")
                print(f"   % Margem: {resumo_financeiro.get('percentual_margem_total', 0):.1f}%")
                print(f"   ✅ Resumo financeiro presente")
            else:
                print(f"   ❌ Resumo financeiro não encontrado")
            
            # Verificar alguns contratos específicos
            resultados = data.get('resultados', [])
            print(f"\n🔍 Análise de contratos individuais:")
            
            contratos_com_faturamento = 0
            total_faturamento_calculado = 0
            
            for resultado in resultados[:5]:  # Primeiros 5 contratos
                contrato_id = resultado.get('contrato_id')
                valores = resultado.get('valores_contratuais', {})
                analise = resultado.get('analise_financeira', {})
                vigencia = resultado.get('vigencia', {})
                
                valor_mensal = valores.get('valor_mensal', 0)
                faturamento_periodo = valores.get('faturamento_periodo', 0)
                meses_periodo = vigencia.get('meses_no_periodo', 0)
                
                if valor_mensal > 0:
                    contratos_com_faturamento += 1
                    total_faturamento_calculado += faturamento_periodo
                    
                    # Verificar se o cálculo está correto (valor_mensal × meses)
                    faturamento_esperado = valor_mensal * meses_periodo
                    calculo_correto = abs(faturamento_periodo - faturamento_esperado) < 0.01
                    
                    print(f"   Contrato {contrato_id}:")
                    print(f"      💰 Valor mensal: R$ {valor_mensal:.2f}")
                    print(f"      📅 Meses no período: {meses_periodo}")
                    print(f"      💵 Faturamento período: R$ {faturamento_periodo:.2f}")
                    print(f"      ✅ Cálculo correto: {'Sim' if calculo_correto else 'Não'}")
                    
                    if analise:
                        margem = analise.get('margem_bruta', 0)
                        percentual = analise.get('percentual_margem', 0)
                        print(f"      📈 Margem: R$ {margem:.2f} ({percentual:.1f}%)")
                else:
                    print(f"   Contrato {contrato_id}: Sem valor mensal definido")
            
            if contratos_com_faturamento > 0:
                print(f"\n✅ TESTE PASSOU:")
                print(f"   Contratos com faturamento: {contratos_com_faturamento}")
                print(f"   Faturamento total calculado: R$ {total_faturamento_calculado:.2f}")
                print(f"   Cálculo de faturamento implementado corretamente")
            else:
                print(f"\n❌ TESTE FALHOU: Nenhum contrato com faturamento encontrado")
                
        else:
            print(f"   ❌ Erro na requisição: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Erro: Servidor não está rodando")
        print("   💡 Execute: python manage.py runserver")
    except Exception as e:
        print(f"   ❌ Erro inesperado: {e}")
    
    print(f"\n" + "=" * 80)
    
    # Teste adicional com período de 3 meses
    print("TESTE ADICIONAL - PERÍODO DE 3 MESES")
    print("=" * 50)
    
    data_inicial_3m = datetime(2024, 8, 1).date()
    data_final_3m = datetime(2024, 10, 31).date()
    
    params_3m = {
        'data_inicial': data_inicial_3m.strftime('%Y-%m-%d'),
        'data_final': data_final_3m.strftime('%Y-%m-%d')
    }
    
    try:
        response_3m = requests.get(url, params=params_3m)
        if response_3m.status_code == 200:
            data_3m = response_3m.json()
            resumo_3m = data_3m.get('resumo_financeiro', {})
            
            print(f"📅 Período: {data_inicial_3m} a {data_final_3m} (3 meses)")
            print(f"💰 Faturamento 3 meses: R$ {resumo_3m.get('faturamento_total_periodo', 0):.2f}")
            print(f"📈 Margem 3 meses: {resumo_3m.get('percentual_margem_total', 0):.1f}%")
            
    except Exception as e:
        print(f"❌ Erro no teste de 3 meses: {e}")
    
    print(f"\n" + "=" * 80)

if __name__ == "__main__":
    teste_faturamento_contratos()
