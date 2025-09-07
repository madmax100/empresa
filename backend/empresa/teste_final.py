#!/usr/bin/env python
"""
✅ TESTE FINAL DO ENDPOINT CORRIGIDO
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.views.access import relatorio_valor_estoque
from django.test import RequestFactory
from django.http import JsonResponse
import json

def teste_final_endpoint():
    """Teste final do endpoint corrigido"""
    
    print("=" * 60)
    print("✅ TESTE FINAL DO ENDPOINT CORRIGIDO")
    print("=" * 60)
    
    try:
        # Criar request simulado
        factory = RequestFactory()
        request = factory.get('/contas/relatorio-valor-estoque/')
        
        # Chamar o endpoint
        print("🔄 Chamando endpoint...")
        response = relatorio_valor_estoque(request)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # Renderizar response
            response.render()
            data = json.loads(response.content.decode('utf-8'))
            
            print(f"✅ SUCESSO! Dados retornados:")
            print(f"  📅 Data posição: {data.get('data_posicao')}")
            print(f"  💰 Valor total: R$ {data.get('valor_total_estoque', 0):,.2f}")
            print(f"  📦 Total produtos: {data.get('total_produtos_em_estoque', 0)}")
            print(f"  📋 Detalhes: {len(data.get('detalhes_por_produto', []))} produtos")
            
            # Mostrar primeiros 5 produtos
            detalhes = data.get('detalhes_por_produto', [])
            if detalhes:
                print(f"\n📦 Primeiros 5 produtos:")
                for i, produto in enumerate(detalhes[:5], 1):
                    print(f"  {i}. {produto.get('produto_descricao', '')[:40]}")
                    print(f"     Qtd: {produto.get('quantidade_em_estoque', 0)} | "
                          f"Custo: R$ {produto.get('custo_unitario', 0):.2f} | "
                          f"Total: R$ {produto.get('valor_total_produto', 0):.2f}")
            
            # Teste com data específica
            print(f"\n🗓️ Testando com data específica (2025-01-01)...")
            request_data = factory.get('/contas/relatorio-valor-estoque/?data=2025-01-01')
            response_data = relatorio_valor_estoque(request_data)
            response_data.render()
            data_historica = json.loads(response_data.content.decode('utf-8'))
            
            print(f"  📅 Data: {data_historica.get('data_posicao')}")
            print(f"  💰 Valor: R$ {data_historica.get('valor_total_estoque', 0):,.2f}")
            print(f"  📦 Produtos: {data_historica.get('total_produtos_em_estoque', 0)}")
            
            print(f"\n🎯 ENDPOINT FUNCIONANDO PERFEITAMENTE!")
            
        else:
            print(f"❌ Erro: Status {response.status_code}")
            print(f"❌ Conteúdo: {response.content}")
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    teste_final_endpoint()
