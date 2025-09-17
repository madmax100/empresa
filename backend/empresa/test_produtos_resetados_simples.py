#!/usr/bin/env python
"""
Teste direto da view ProdutosResetadosViewSet usando Django shell.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from rest_framework.test import APIRequestFactory
from rest_framework.request import Request
from django.contrib.auth.models import AnonymousUser
from contas.views.produtos_resetados_view import ProdutosResetadosViewSet

def test_produtos_resetados():
    """Testa a view ProdutosResetadosViewSet."""
    print("=== TESTE DA VIEW PRODUTOS_RESETADOS ===\n")
    
    # Criar uma instância do factory para requests
    factory = APIRequestFactory()
    
    # Criar uma request GET
    request = factory.get('/api/produtos-resetados/', {
        'meses': '12',
        'limite': '10',
        'offset': '0',
        'ordem': 'data_reset',
        'reverso': 'true'
    })
    
    # Configurar o usuário 
    request.user = AnonymousUser()
    
    # Criar uma instância do ViewSet
    viewset = ProdutosResetadosViewSet()
    viewset.request = Request(request)
    
    try:
        # Chamar o método list
        response = viewset.list(viewset.request)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.data
            print(f"Sucesso: {data.get('success', False)}")
            
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
            
            # Mostrar produtos
            produtos = data.get('data', [])
            print(f"\n=== PRODUTOS RESETADOS ({len(produtos)} produtos) ===")
            for i, produto in enumerate(produtos):
                print(f"{i+1:2d}. {produto.get('codigo', 'N/A'):4s} - {produto.get('nome', 'N/A')[:40]:<40}")
                print(f"     Data Reset: {produto.get('data_reset')} | Qtd: {produto.get('quantidade_reset'):6.1f} | Atual: {produto.get('estoque_atual'):6.1f} | Valor: R$ {produto.get('valor_atual'):8.2f}")
                
        else:
            print(f"Erro: {response.data}")
            
    except Exception as e:
        print(f"Erro ao executar teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_produtos_resetados()