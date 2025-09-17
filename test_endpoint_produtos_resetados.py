#!/usr/bin/env python
"""
Script para testar o endpoint produtos_resetados via Django shell.
"""

import os
import sys
import django
from pathlib import Path

# Adiciona o diretório do projeto ao path
project_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(project_dir))

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from rest_framework.test import APIRequestFactory
from rest_framework.request import Request
from django.contrib.auth.models import AnonymousUser
from empresa.contas.views.estoque_views import EstoqueViewSet

def test_produtos_resetados_endpoint():
    """Testa o endpoint produtos_resetados."""
    print("=== TESTE DO ENDPOINT PRODUTOS_RESETADOS ===\n")
    
    # Criar uma instância do factory para requests
    factory = APIRequestFactory()
    
    # Criar uma request GET
    request = factory.get('/api/estoque/produtos_resetados/', {
        'meses': '12',
        'limite': '20',
        'offset': '0',
        'ordem': 'data_reset',
        'reverso': 'true'
    })
    
    # Configurar o usuário (necessário para o Django REST framework)
    request.user = AnonymousUser()
    
    # Criar uma instância do ViewSet
    viewset = EstoqueViewSet()
    viewset.request = Request(request)
    
    try:
        # Chamar o método produtos_resetados
        response = viewset.produtos_resetados(viewset.request)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Data Keys: {list(response.data.keys())}")
        
        if response.status_code == 200:
            data = response.data
            print(f"\nSucesso: {data.get('success', False)}")
            print(f"Total de registros: {data.get('meta', {}).get('total_registros', 0)}")
            
            # Mostrar estatísticas
            stats = data.get('estatisticas', {})
            print(f"\n=== ESTATÍSTICAS ===")
            print(f"Total produtos resetados: {stats.get('total_produtos_resetados', 0)}")
            print(f"Produtos ativos: {stats.get('produtos_ativos', 0)}")
            print(f"Produtos com estoque: {stats.get('produtos_com_estoque', 0)}")
            print(f"Valor total do estoque: R$ {stats.get('valor_total_estoque', 0):,.2f}")
            print(f"Data limite: {stats.get('data_limite', 'N/A')}")
            
            # Mostrar resets por mês
            resets_mes = stats.get('resets_por_mes', {})
            if resets_mes:
                print(f"\n=== RESETS POR MÊS ===")
                for mes, count in sorted(resets_mes.items()):
                    print(f"  {mes}: {count} produtos")
            
            # Mostrar primeiros produtos
            produtos = data.get('data', [])
            if produtos:
                print(f"\n=== PRIMEIROS 5 PRODUTOS ===")
                for i, produto in enumerate(produtos[:5]):
                    print(f"{i+1}. {produto.get('codigo', 'N/A')} - {produto.get('nome', 'N/A')}")
                    print(f"   Grupo: {produto.get('grupo_nome', 'N/A')}")
                    print(f"   Data Reset: {produto.get('data_reset', 'N/A')}")
                    print(f"   Qtd Reset: {produto.get('quantidade_reset', 0)}")
                    print(f"   Estoque Atual: {produto.get('estoque_atual', 0)}")
                    print(f"   Valor Atual: R$ {produto.get('valor_atual', 0):,.2f}")
                    print()
        else:
            print(f"Erro: {response.data}")
            
    except Exception as e:
        print(f"Erro ao executar teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_produtos_resetados_endpoint()