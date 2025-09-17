#!/usr/bin/env python3
"""
Teste final dos endpoints de estoque
"""

import requests
import json

def testar_endpoints():
    base_url = "http://127.0.0.1:8000/api/estoque-controle"
    
    print("=== TESTE DOS ENDPOINTS DE ESTOQUE ===\n")
    
    # Teste 1: Endpoint estoque_atual
    print("1. Teste endpoint estoque_atual (primeiros 5 produtos):")
    try:
        response = requests.get(f"{base_url}/estoque_atual/?limite=5")
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {response.status_code}")
            print(f"Total de produtos: {len(data.get('results', []))}")
            
            for produto in data.get('results', [])[:3]:
                print(f"  - {produto.get('nome')}: {produto.get('quantidade_atual')} unidades (R$ {produto.get('valor_atual', 0):,.2f})")
        else:
            print(f"Erro: {response.status_code}")
    except Exception as e:
        print(f"Erro na requisição: {e}")
    
    print("\n" + "="*50)
    
    # Teste 2: Endpoint valor_estoque_por_grupo
    print("2. Teste endpoint valor_estoque_por_grupo:")
    try:
        response = requests.get(f"{base_url}/valor_estoque_por_grupo/")
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {response.status_code}")
            
            grupos = data.get('estoque_por_grupo', [])
            valor_total = sum(grupo.get('valor_total_estoque', 0) for grupo in grupos)
            print(f"Valor total do estoque: R$ {valor_total:,.2f}")
            print(f"Número de grupos: {len(grupos)}")
            
            # Mostrar os 3 grupos com maior valor
            grupos_ordenados = sorted(grupos, key=lambda x: x.get('valor_total_estoque', 0), reverse=True)
            print("Top 3 grupos por valor:")
            for grupo in grupos_ordenados[:3]:
                print(f"  - {grupo.get('grupo_nome', 'N/A')}: R$ {grupo.get('valor_total_estoque', 0):,.2f}")
        else:
            print(f"Erro: {response.status_code}")
    except Exception as e:
        print(f"Erro na requisição: {e}")
    
    print("\n" + "="*50)
    
    # Teste 3: Produto específico que testamos
    print("3. Teste produto específico (2867):")
    try:
        response = requests.get(f"{base_url}/estoque_atual/?produto_id=2867")
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                produto = data['results'][0]
                print(f"Produto: {produto.get('nome')}")
                print(f"Estoque: {produto.get('quantidade_atual')}")
                print(f"Valor unitário: R$ {produto.get('custo_unitario_atual', 0):,.2f}")
                print(f"Valor total: R$ {produto.get('valor_atual', 0):,.2f}")
        else:
            print(f"Erro: {response.status_code}")
    except Exception as e:
        print(f"Erro na requisição: {e}")

if __name__ == "__main__":
    testar_endpoints()