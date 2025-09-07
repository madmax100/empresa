#!/usr/bin/env python3
"""
Script para diagnosticar o problema de estoque vazio
"""

import requests
import json
from datetime import date, datetime

def test_endpoint(url, nome):
    print(f"\n🔍 Testando: {nome}")
    print(f"URL: {url}")
    print("-" * 40)
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Tipo: {type(data)}")
            
            if isinstance(data, list):
                print(f"Total de itens: {len(data)}")
                if len(data) > 0:
                    print("Primeiro item:")
                    print(json.dumps(data[0], indent=2, ensure_ascii=False, default=str))
            elif isinstance(data, dict):
                if 'results' in data:
                    results = data['results']
                    count = data.get('count', len(results))
                    print(f"Total (count): {count}")
                    print(f"Resultados retornados: {len(results)}")
                    if len(results) > 0:
                        print("Primeiro resultado:")
                        print(json.dumps(results[0], indent=2, ensure_ascii=False, default=str))
                else:
                    print(f"Chaves disponíveis: {list(data.keys())}")
                    print("Dados:")
                    print(json.dumps(data, indent=2, ensure_ascii=False, default=str)[:500] + "...")
        else:
            print(f"Erro: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print("❌ Timeout na requisição")
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - servidor pode estar offline")
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    base_url = "http://localhost:8000/contas"
    
    print("🔍 DIAGNÓSTICO DETALHADO DO ESTOQUE")
    print("=" * 50)
    
    # 1. Testar endpoint de produtos
    test_endpoint(f"{base_url}/produtos/?limit=3", "Produtos")
    
    # 2. Testar saldos de estoque
    test_endpoint(f"{base_url}/saldos_estoque/?limit=3", "Saldos de Estoque")
    
    # 3. Testar movimentações
    test_endpoint(f"{base_url}/movimentacoes_estoque/?limit=3", "Movimentações de Estoque")
    
    # 4. Testar posições
    test_endpoint(f"{base_url}/posicoes_estoque/?limit=3", "Posições de Estoque")
    
    # 5. Testar relatório de valor
    test_endpoint(f"{base_url}/relatorio-valor-estoque/?data=2025-09-01", "Relatório de Valor")
    
    # 6. Verificar se há saldos com quantidade > 0
    test_endpoint(f"{base_url}/saldos_estoque/?quantidade__gt=0&limit=5", "Saldos com Quantidade > 0")
    
    # 7. Verificar movimentações de hoje
    hoje = date.today().strftime("%Y-%m-%d")
    test_endpoint(f"{base_url}/movimentacoes_estoque/?data_movimentacao__date={hoje}&limit=3", f"Movimentações de {hoje}")
    
    print("\n✅ Diagnóstico concluído!")

if __name__ == "__main__":
    main()
