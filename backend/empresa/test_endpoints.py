#!/usr/bin/env python
"""
Script para testar endpoints do fluxo-caixa-lucro
"""
import requests
import json
import sys
from datetime import date, timedelta

BASE_URL = "http://127.0.0.1:8000/api/fluxo-caixa-lucro"

# Lista de endpoints para testar
ENDPOINTS = [
    {"url": "", "method": "GET", "name": "Lista principal"},
    {"url": "/dashboard/", "method": "GET", "name": "Dashboard"},
    {"url": "/estatisticas/", "method": "GET", "name": "Estatísticas"},
    {"url": "/indicadores/", "method": "GET", "name": "Indicadores"},
    {"url": "/alertas_inteligentes/", "method": "GET", "name": "Alertas Inteligentes"},
    {"url": "/projecao_fluxo/", "method": "GET", "name": "Projeção de Fluxo"},
    {"url": "/relatorio_dre/", "method": "GET", "name": "Relatório DRE"},
    {"url": "/relatorio_diario/", "method": "GET", "name": "Relatório Diário"},
    {"url": "/previsao_saldo/", "method": "GET", "name": "Previsão de Saldo"},
    {"url": "/analise_categorias/", "method": "GET", "name": "Análise de Categorias"},
    {"url": "/analise_contratos/", "method": "GET", "name": "Análise de Contratos"},
    {"url": "/alertas/", "method": "GET", "name": "Alertas"},
]

def test_endpoint(endpoint_info):
    """Testa um endpoint específico"""
    url = f"{BASE_URL}{endpoint_info['url']}"
    method = endpoint_info['method']
    name = endpoint_info['name']
    
    print(f"\n{'='*60}")
    print(f"Testando: {name}")
    print(f"URL: {url}")
    print(f"Método: {method}")
    print(f"{'='*60}")
    
    try:
        # Adiciona parâmetros de data para alguns endpoints
        params = {}
        if any(x in endpoint_info['url'] for x in ['relatorio_dre', 'relatorio_diario']):
            hoje = date.today()
            params = {
                'data_inicial': (hoje - timedelta(days=30)).strftime('%Y-%m-%d'),
                'data_final': hoje.strftime('%Y-%m-%d')
            }
        
        if method == "GET":
            response = requests.get(url, params=params, timeout=30)
        elif method == "POST":
            response = requests.post(url, json={}, timeout=30)
        else:
            print(f"❌ Método {method} não suportado")
            return
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCESSO!")
            try:
                data = response.json()
                print(f"Tipo de resposta: {type(data)}")
                if isinstance(data, dict):
                    print(f"Chaves principais: {list(data.keys())}")
                    # Mostra um preview dos dados
                    preview = {}
                    for key, value in list(data.items())[:3]:  # Apenas primeiras 3 chaves
                        if isinstance(value, (dict, list)):
                            preview[key] = f"{type(value).__name__} com {len(value)} itens"
                        else:
                            preview[key] = str(value)[:100]  # Limita string longa
                    print(f"Preview dos dados: {json.dumps(preview, indent=2, ensure_ascii=False)}")
                elif isinstance(data, list):
                    print(f"Lista com {len(data)} itens")
                    if data:
                        print(f"Primeiro item: {json.dumps(data[0], indent=2, ensure_ascii=False)[:200]}...")
            except json.JSONDecodeError:
                print("Resposta não é JSON válido")
                print(f"Conteúdo: {response.text[:200]}...")
        elif response.status_code == 404:
            print("❌ ENDPOINT NÃO ENCONTRADO")
        elif response.status_code == 500:
            print("❌ ERRO INTERNO DO SERVIDOR")
            try:
                error_data = response.json()
                print(f"Erro: {error_data}")
            except:
                print("Não foi possível decodificar o erro")
        else:
            print(f"❌ ERRO - Status: {response.status_code}")
            print(f"Resposta: {response.text[:200]}...")
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT - Endpoint demorou muito para responder")
    except requests.exceptions.ConnectionError:
        print("❌ ERRO DE CONEXÃO - Servidor não está respondendo")
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {str(e)}")

def main():
    """Função principal"""
    print("🧪 TESTE DE ENDPOINTS - FLUXO CAIXA LUCRO")
    print(f"Base URL: {BASE_URL}")
    
    # Testa se o servidor está respondendo
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        print(f"✅ Servidor Django está rodando (Status: {response.status_code})")
    except:
        print("❌ Servidor Django não está respondendo!")
        sys.exit(1)
    
    # Testa todos os endpoints
    resultados = {}
    for endpoint in ENDPOINTS:
        try:
            test_endpoint(endpoint)
            resultados[endpoint['name']] = "Testado"
        except KeyboardInterrupt:
            print("\n⚠️ Teste interrompido pelo usuário")
            break
        except Exception as e:
            print(f"❌ Erro ao testar {endpoint['name']}: {str(e)}")
            resultados[endpoint['name']] = f"Erro: {str(e)}"
    
    # Resumo final
    print(f"\n{'='*60}")
    print("📊 RESUMO DOS TESTES")
    print(f"{'='*60}")
    for name, status in resultados.items():
        print(f"{name}: {status}")
    
    print(f"\n🎯 Total de endpoints testados: {len(resultados)}")

if __name__ == "__main__":
    main()
