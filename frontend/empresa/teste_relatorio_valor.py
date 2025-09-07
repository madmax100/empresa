#!/usr/bin/env python3
"""
Teste específico do endpoint relatorio-valor-estoque baseado na documentação
"""

import requests
import json
from datetime import date

def test_relatorio_valor_estoque():
    base_url = "http://localhost:8000/contas"
    
    print("🔍 TESTANDO ENDPOINT: relatorio-valor-estoque")
    print("=" * 50)
    
    # URLs para testar baseadas na documentação
    urls_teste = [
        f"{base_url}/relatorio-valor-estoque/",
        f"{base_url}/relatorio-valor-estoque/?data=2025-09-02",
        f"{base_url}/relatorio-valor-estoque/?data=2025-01-01",
    ]
    
    for url in urls_teste:
        print(f"\n🔗 Testando: {url}")
        try:
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Sucesso!")
                
                # Verificar campos esperados baseados na documentação
                campos_esperados = ['data_posicao', 'valor_total_estoque', 'total_produtos_em_estoque']
                for campo in campos_esperados:
                    if campo in data:
                        print(f"   📊 {campo}: {data[campo]}")
                    else:
                        print(f"   ⚠️  Campo {campo} não encontrado")
                
                # Mostrar estrutura básica
                print(f"   📋 Chaves disponíveis: {list(data.keys())}")
                
            elif response.status_code == 404:
                print(f"   ❌ Endpoint não encontrado (404)")
            elif response.status_code == 500:
                print(f"   ❌ Erro interno do servidor (500)")
                print(f"   📄 Detalhes: {response.text[:200]}...")
            else:
                print(f"   ⚠️  Status inesperado: {response.status_code}")
                print(f"   📄 Resposta: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Erro de conexão - servidor Django pode estar offline")
        except requests.exceptions.Timeout:
            print(f"   ❌ Timeout na requisição")
        except Exception as e:
            print(f"   ❌ Erro: {e}")

def test_endpoints_funcionais():
    base_url = "http://localhost:8000/contas"
    
    print("\n\n🔍 TESTANDO ENDPOINTS FUNCIONAIS")
    print("=" * 50)
    
    # Endpoints que devem funcionar baseados na documentação
    endpoints_funcionais = [
        ("/saldos_estoque/", "Saldos de Estoque"),
        ("/movimentacoes_estoque/", "Movimentações de Estoque"),
        ("/produtos/", "Produtos"),
        ("/tipos_movimentacao_estoque/", "Tipos de Movimentação"),
    ]
    
    for endpoint, nome in endpoints_funcionais:
        print(f"\n📋 {nome}")
        url = f"{base_url}{endpoint}?limit=1"
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'count' in data:
                    print(f"   ✅ {data.get('count', 0)} registros encontrados")
                elif isinstance(data, list):
                    print(f"   ✅ {len(data)} registros encontrados")
                else:
                    print(f"   ✅ Endpoint funcionando")
            else:
                print(f"   ❌ Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")

if __name__ == "__main__":
    test_relatorio_valor_estoque()
    test_endpoints_funcionais()
    print("\n✅ Teste concluído!")
