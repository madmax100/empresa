#!/usr/bin/env python
"""
Script para testar o endpoint de custos variáveis
"""

import requests
import json
from datetime import datetime, timedelta

# Configurações
BASE_URL = "http://127.0.0.1:8000"
ENDPOINT = "/contas/relatorios/custos-variaveis/"

def test_custos_variaveis():
    """Testa o endpoint de custos variáveis"""
    
    # Definir período de teste (últimos 30 dias)
    data_fim = datetime.now().date()
    data_inicio = data_fim - timedelta(days=30)
    
    # Parâmetros da requisição
    params = {
        'data_inicio': data_inicio.strftime('%Y-%m-%d'),
        'data_fim': data_fim.strftime('%Y-%m-%d')
    }
    
    # URL completa
    url = f"{BASE_URL}{ENDPOINT}"
    
    print(f"🔍 Testando endpoint: {url}")
    print(f"📅 Período: {params['data_inicio']} a {params['data_fim']}")
    print("-" * 60)
    
    try:
        # Fazer requisição
        response = requests.get(url, params=params)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Requisição bem-sucedida!")
            print(f"📈 Total de contas pagas: {data.get('total_contas_pagas', 0)}")
            print(f"💰 Total valor pago: R$ {data.get('totais_gerais', {}).get('total_valor_pago', 0):,.2f}")
            
            # Estatísticas de fornecedores
            stats = data.get('estatisticas_fornecedores', {})
            print(f"🏪 Fornecedores variáveis cadastrados: {stats.get('total_fornecedores_variaveis_cadastrados', 0)}")
            print(f"🏪 Fornecedores com pagamentos: {stats.get('fornecedores_com_pagamentos_no_periodo', 0)}")
            
            # Resumo por especificação
            resumo_especificacao = data.get('resumo_por_especificacao', [])
            print(f"\n📋 Resumo por Especificação ({len(resumo_especificacao)} categorias):")
            
            for i, spec in enumerate(resumo_especificacao[:5]):  # Mostrar apenas top 5
                print(f"  {i+1}. {spec['especificacao']}: R$ {spec['valor_pago_total']:,.2f}")
                print(f"     └─ {spec['quantidade_contas']} contas de {spec['quantidade_fornecedores']} fornecedor(es)")
            
            if len(resumo_especificacao) > 5:
                print(f"     ... e mais {len(resumo_especificacao) - 5} especificações")
            
            # Algumas contas detalhadas
            contas = data.get('contas_pagas', [])
            if contas:
                print(f"\n💳 Exemplos de Contas Pagas (primeiras 3 de {len(contas)}):")
                for i, conta in enumerate(contas[:3]):
                    print(f"  {i+1}. {conta['fornecedor_nome']} - R$ {conta['valor_pago']:,.2f}")
                    print(f"     └─ Especificação: {conta['fornecedor_especificacao']}")
                    print(f"     └─ Data: {conta['data_pagamento']}")
            
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📝 Detalhes do erro: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"📝 Resposta: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão. Verifique se o servidor Django está rodando.")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_custos_variaveis()
