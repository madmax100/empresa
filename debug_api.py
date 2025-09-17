#!/usr/bin/env python3
"""
Debug da resposta da API
"""

import requests
import json

def debug_api():
    base_url = "http://127.0.0.1:8000/api/estoque-controle"
    
    print("=== DEBUG DA API ===\n")
    
    # Teste endpoint estoque_atual
    print("1. Debug endpoint estoque_atual:")
    try:
        response = requests.get(f"{base_url}/estoque_atual/?limite=2")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                print(f"Raw response (first 500 chars): {response.text[:500]}")
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print(f"Raw response: {response.text}")
        else:
            print(f"Response text: {response.text}")
    except Exception as e:
        print(f"Erro na requisição: {e}")
    
    print("\n" + "="*50)
    
    # Teste valor_estoque_por_grupo
    print("2. Debug endpoint valor_estoque_por_grupo:")
    try:
        response = requests.get(f"{base_url}/valor_estoque_por_grupo/")
        print(f"Status: {response.status_code}")
        print(f"Raw response: {response.text}")
    except Exception as e:
        print(f"Erro na requisição: {e}")

if __name__ == "__main__":
    debug_api()