#!/usr/bin/env python3
"""
Script de debug detalhado para verificar estrutura de dados dos endpoints
"""

import requests
import json
from datetime import date

def debug_endpoint(url, nome):
    print(f"\n🔍 DEBUGANDO: {nome}")
    print("=" * 50)
    print(f"URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Tipo de resposta: {type(data)}")
            
            if isinstance(data, list):
                print(f"Total de itens: {len(data)}")
                if len(data) > 0:
                    print("Estrutura do primeiro item:")
                    print(json.dumps(data[0], indent=2, ensure_ascii=False))
            else:
                print(f"Chaves disponíveis: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
                if 'results' in data:
                    print(f"Total de itens: {data.get('count', len(data['results']))}")
                    if len(data['results']) > 0:
                        print("Estrutura do primeiro item:")
                        print(json.dumps(data['results'][0], indent=2, ensure_ascii=False))
        else:
            print(f"Erro: {response.text[:200]}...")
            
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    base_url = "http://localhost:8000/contas"
    
    # 1. Saldos Estoque
    debug_endpoint(f"{base_url}/saldos_estoque/?limit=2", "Saldos Estoque")
    
    # 2. Movimentações
    debug_endpoint(f"{base_url}/movimentacoes_estoque/?limit=2", "Movimentações Estoque")
    
    # 3. Posições
    debug_endpoint(f"{base_url}/posicoes_estoque/?limit=2", "Posições Estoque")
    
    # 4. Produtos
    debug_endpoint(f"{base_url}/produtos/?limit=2", "Produtos")
    
    print("\n✅ Debug concluído!")
