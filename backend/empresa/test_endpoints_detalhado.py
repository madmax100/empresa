#!/usr/bin/env python
"""
Script detalhado para verificar os erros dos endpoints
"""
import requests
import json
from datetime import date, timedelta

BASE_URL = "http://127.0.0.1:8000/api/fluxo-caixa-lucro"

def test_detailed_endpoint(url, name):
    """Testa um endpoint específico com mais detalhes"""
    print(f"{'='*50}")
    print(f"Testando: {name}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCESSO!")
            try:
                data = response.json()
                print("Estrutura da resposta:")
                if isinstance(data, dict):
                    for key, value in data.items():
                        print(f"  {key}: {type(value).__name__}")
                        if isinstance(value, (dict, list)) and value:
                            if isinstance(value, dict):
                                print(f"    Subchaves: {list(value.keys())[:3]}")
                            else:
                                print(f"    {len(value)} itens")
                elif isinstance(data, list):
                    print(f"  Lista com {len(data)} itens")
                    if data:
                        print(f"  Primeiro item: {type(data[0]).__name__}")
            except json.JSONDecodeError:
                print("❌ Resposta não é JSON válido")
                print(f"Conteúdo: {response.text[:200]}...")
        else:
            print(f"❌ ERRO - Status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Erro JSON: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Erro texto: {response.text[:300]}...")
                
    except Exception as e:
        print(f"❌ EXCEÇÃO: {str(e)}")

def main():
    """Testa endpoints detalhadamente"""
    print("🔍 ANÁLISE DETALHADA DOS ENDPOINTS")
    
    endpoints = [
        ("/dashboard/", "Dashboard"),
        ("/estatisticas/", "Estatísticas"), 
        ("/indicadores/", "Indicadores"),
        ("/alertas_inteligentes/", "Alertas Inteligentes"),
        ("/projecao_fluxo/", "Projeção de Fluxo"),
        ("/relatorio_dre/?data_inicial=2025-08-01&data_final=2025-09-06", "Relatório DRE com parâmetros"),
        ("/relatorio_diario/?data=2025-09-06", "Relatório Diário com data"),
        ("/analise_categorias/", "Análise de Categorias"),
        ("/cenarios/", "Cenários"),
    ]
    
    for endpoint_url, name in endpoints:
        test_detailed_endpoint(f"{BASE_URL}{endpoint_url}", name)
        print()

if __name__ == "__main__":
    main()
