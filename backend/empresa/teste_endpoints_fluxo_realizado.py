#!/usr/bin/env python
"""
Script para testar os novos endpoints de fluxo de caixa realizado
"""
import requests
import json
from datetime import date, timedelta

BASE_URL = "http://127.0.0.1:8000/api"

def test_endpoint(endpoint, params=None):
    """Testa um endpoint e exibe o resultado"""
    url = f"{BASE_URL}/{endpoint}/"
    
    print(f"\n{'='*60}")
    print(f"Testando: {endpoint}")
    print(f"URL: {url}")
    if params:
        print(f"Parâmetros: {params}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Resposta (estrutura):")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print("Erro na resposta:")
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão: {e}")
    except Exception as e:
        print(f"Erro: {e}")

def main():
    print("Testando os novos endpoints de Fluxo de Caixa Realizado")
    print("Aguarde...")
    
    # Definir datas para teste
    data_inicio = (date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
    data_fim = date.today().strftime('%Y-%m-%d')
    
    params_periodo = {
        'data_inicio': data_inicio,
        'data_fim': data_fim
    }
    
    # Teste 1: Movimentações realizadas
    test_endpoint(
        "fluxo-caixa-realizado/movimentacoes_realizadas",
        params_periodo
    )
    
    # Teste 2: Resumo mensal
    test_endpoint(
        "fluxo-caixa-realizado/resumo_mensal",
        params_periodo
    )
    
    # Teste 3: Resumo diário
    test_endpoint(
        "fluxo-caixa-realizado/resumo_diario",
        params_periodo
    )
    
    # Teste 4: Movimentações com vencimento em aberto
    test_endpoint(
        "fluxo-caixa-realizado/movimentacoes_vencimento_aberto",
        params_periodo
    )
    
    # Teste 5: Comparativo realizado vs previsto
    test_endpoint(
        "analise-fluxo-caixa/comparativo_realizado_vs_previsto",
        params_periodo
    )
    
    # Teste 6: Análise de inadimplência
    test_endpoint(
        "analise-fluxo-caixa/inadimplencia",
        {'data_limite': date.today().strftime('%Y-%m-%d')}
    )
    
    # Teste 7: Projeção semanal
    test_endpoint(
        "analise-fluxo-caixa/projecao_semanal",
        {'semanas': 4}
    )
    
    print(f"\n{'='*60}")
    print("Teste concluído!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
