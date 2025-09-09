#!/usr/bin/env python3
"""
Teste para verificar se o endpoint suprimentos-por-contrato
está retornando corretamente os valores mensais dos contratos
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

from contas.models.access import ContratosLocacao

def teste_valores_contratuais():
    """
    Testa se o endpoint retorna os valores contratuais corretamente
    """
    print("=" * 80)
    print("TESTE DE VALORES CONTRATUAIS - ENDPOINT SUPRIMENTOS POR CONTRATO")
    print("=" * 80)
    
    # Buscar alguns contratos para análise
    contratos_sample = ContratosLocacao.objects.filter(
        valorpacela__isnull=False,
        valorpacela__gt=0
    )[:5]
    
    print(f"\n📋 Análise de contratos com valores:")
    for contrato in contratos_sample:
        print(f"   Contrato {contrato.id}: Valor mensal = R$ {contrato.valorpacela or 0}")
        print(f"      Total: R$ {contrato.valorcontrato or 0} | Parcelas: {contrato.numeroparcelas}")
        print(f"      Vigência: {contrato.inicio} até {contrato.fim or 'ativo'}")
    
    # Definir período de teste
    hoje = datetime.now().date()
    data_inicial = hoje - timedelta(days=30)
    data_final = hoje + timedelta(days=30)
    
    # Teste do endpoint
    url = "http://localhost:8000/api/contratos_locacao/suprimentos/"
    params = {
        'data_inicial': data_inicial.strftime('%Y-%m-%d'),
        'data_final': data_final.strftime('%Y-%m-%d')
    }
    
    print(f"\n🔗 Testando endpoint com valores contratuais:")
    print(f"   URL: {url}")
    print(f"   Período: {data_inicial} a {data_final}")
    
    try:
        response = requests.get(url, params=params)
        
        print(f"\n📊 Resultado do teste:")
        print(f"   Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            resultados = data.get('resultados', [])
            print(f"   Contratos retornados: {len(resultados)}")
            
            # Verificar se os valores contratuais estão presentes
            contratos_com_valores = 0
            total_valor_mensal = 0
            
            print(f"\n🔍 Verificação de valores contratuais:")
            
            for resultado in resultados[:10]:  # Primeiros 10 contratos
                contrato_id = resultado.get('contrato_id')
                valores = resultado.get('valores_contratuais', {})
                
                if valores:
                    valor_mensal = valores.get('valor_mensal', 0)
                    valor_total = valores.get('valor_total_contrato', 0)
                    parcelas = valores.get('numero_parcelas', 'N/A')
                    
                    if valor_mensal > 0:
                        contratos_com_valores += 1
                        total_valor_mensal += valor_mensal
                        
                    print(f"   Contrato {contrato_id}:")
                    print(f"      💰 Valor mensal: R$ {valor_mensal}")
                    print(f"      📊 Valor total: R$ {valor_total}")
                    print(f"      📅 Parcelas: {parcelas}")
                else:
                    print(f"   Contrato {contrato_id}: ❌ Valores contratuais não encontrados")
            
            if contratos_com_valores > 0:
                print(f"\n✅ TESTE PASSOU:")
                print(f"   Contratos com valores: {contratos_com_valores}")
                print(f"   Valor mensal total: R$ {total_valor_mensal:.2f}")
                print(f"   Média mensal por contrato: R$ {total_valor_mensal/contratos_com_valores:.2f}")
            else:
                print(f"\n❌ TESTE FALHOU: Nenhum contrato com valores encontrado")
                
        else:
            print(f"   ❌ Erro na requisição: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Erro: Servidor não está rodando")
        print("   💡 Execute: python manage.py runserver")
    except Exception as e:
        print(f"   ❌ Erro inesperado: {e}")
    
    print(f"\n" + "=" * 80)

if __name__ == "__main__":
    teste_valores_contratuais()
