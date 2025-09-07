#!/usr/bin/env python
"""
Script simplificado para testar endpoints do fluxo-caixa-lucro
"""
import requests
import json
from datetime import date, timedelta

BASE_URL = "http://127.0.0.1:8000/api/fluxo-caixa-lucro"

# Lista dos principais endpoints para testar
ENDPOINTS = [
    {"url": "/dashboard/", "name": "Dashboard"},
    {"url": "/estatisticas/", "name": "Estatísticas"},
    {"url": "/indicadores/", "name": "Indicadores"},
    {"url": "/alertas_inteligentes/", "name": "Alertas Inteligentes"},
    {"url": "/projecao_fluxo/", "name": "Projeção de Fluxo"},
    {"url": "/relatorio_dre/", "name": "Relatório DRE"},
    {"url": "/relatorio_diario/", "name": "Relatório Diário"},
]

def test_endpoint(endpoint_info):
    """Testa um endpoint específico"""
    url = f"{BASE_URL}{endpoint_info['url']}"
    name = endpoint_info['name']
    
    print(f"{'='*40}")
    print(f"Testando: {name}")
    print(f"URL: {url}")
    
    try:
        params = {}
        if 'relatorio' in endpoint_info['url']:
            hoje = date.today()
            params = {
                'data_inicial': (hoje - timedelta(days=30)).strftime('%Y-%m-%d'),
                'data_final': hoje.strftime('%Y-%m-%d')
            }
        
        response = requests.get(url, params=params, timeout=10)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCESSO!")
            try:
                data = response.json()
                if isinstance(data, dict):
                    print(f"Chaves: {list(data.keys())[:5]}")  # Apenas primeiras 5 chaves
                elif isinstance(data, list):
                    print(f"Lista com {len(data)} itens")
                return True
            except:
                print("Resposta não é JSON válido")
                return False
        elif response.status_code == 404:
            print("❌ NÃO ENCONTRADO")
            return False
        elif response.status_code == 500:
            print("❌ ERRO INTERNO")
            return False
        else:
            print(f"❌ ERRO - Status: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE RÁPIDO DOS ENDPOINTS")
    
    sucessos = 0
    total = len(ENDPOINTS)
    
    for endpoint in ENDPOINTS:
        if test_endpoint(endpoint):
            sucessos += 1
        print()  # Linha em branco
    
    print(f"{'='*40}")
    print(f"📊 RESULTADO FINAL")
    print(f"Sucessos: {sucessos}/{total}")
    print(f"Taxa de sucesso: {(sucessos/total)*100:.1f}%")

if __name__ == "__main__":
    main()
