#!/usr/bin/env python
"""
Teste do endpoint através da URL completa.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from rest_framework.test import APIClient
from django.test import TestCase

def test_produtos_resetados_endpoint():
    """Testa o endpoint /api/produtos-resetados/ via APIClient."""
    print("=== TESTE DO ENDPOINT /api/produtos-resetados/ ===\n")
    
    client = APIClient()
    
    try:
        # Fazer requisição GET para o endpoint
        response = client.get('/api/produtos-resetados/', {
            'meses': '12',
            'limite': '5',
            'offset': '0',
            'ordem': 'data_reset',
            'reverso': 'true'
        })
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Sucesso: {data.get('success', False)}")
            
            # Mostrar estatísticas
            stats = data.get('estatisticas', {})
            print(f"\n=== ESTATÍSTICAS ===")
            print(f"Total produtos resetados: {stats.get('total_produtos_resetados', 0)}")
            print(f"Produtos ativos: {stats.get('produtos_ativos', 0)}")
            print(f"Produtos com estoque: {stats.get('produtos_com_estoque', 0)}")
            print(f"Valor total do estoque: R$ {stats.get('valor_total_estoque', 0):,.2f}")
            
            # Mostrar produtos
            produtos = data.get('data', [])
            print(f"\n=== PRODUTOS RESETADOS ({len(produtos)} produtos) ===")
            for i, produto in enumerate(produtos):
                print(f"{i+1}. {produto.get('codigo', 'N/A')} - {produto.get('nome', 'N/A')[:50]}")
                print(f"   Data Reset: {produto.get('data_reset')} | Estoque: {produto.get('estoque_atual')}")
                
        else:
            print(f"Erro: {response.json()}")
            
    except Exception as e:
        print(f"Erro ao executar teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_produtos_resetados_endpoint()