#!/usr/bin/env python
"""
🧪 TESTE FINAL DO ENDPOINT CORRIGIDO
"""
import requests
import json

def testar_endpoint_corrigido():
    """Testa o endpoint com as correções aplicadas"""
    print("=" * 70)
    print("🧪 TESTANDO ENDPOINT CORRIGIDO")
    print("=" * 70)
    
    try:
        # Testar o endpoint principal
        url = "http://localhost:8000/contas/relatorio-valor-estoque/"
        
        print(f"🌐 Testando: {url}")
        
        response = requests.get(url, timeout=30)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"💰 Valor total: R$ {data.get('valor_total_estoque', 0):,.2f}")
            print(f"📦 Total de produtos: {data.get('total_produtos_em_estoque', 0)}")
            
            produtos = data.get('detalhes_por_produto', [])
            
            print()
            print("🎯 PRIMEIROS 10 PRODUTOS (VIA ENDPOINT):")
            
            for i, produto in enumerate(produtos[:10]):
                print(f"  {i+1}. ID: {produto['produto_id']}")
                print(f"      📝 Nome: '{produto['produto_descricao']}'")
                print(f"      📊 Saldo: {produto['quantidade_em_estoque']}")
                print(f"      💵 Valor: R$ {produto['valor_total_produto']:,.2f}")
                print()
            
            # Verificar se os nomes estão aparecendo corretamente
            nomes_validos = 0
            nomes_problematicos = 0
            
            for produto in produtos:
                nome = produto['produto_descricao']
                if nome and nome != 'Produto não identificado' and nome != 'None' and nome.strip():
                    nomes_validos += 1
                else:
                    nomes_problematicos += 1
                    print(f"❌ PROBLEMA: Produto {produto['produto_id']} com nome '{nome}'")
            
            print("🔍 ANÁLISE DOS NOMES:")
            print(f"  ✅ Nomes válidos: {nomes_validos}")
            print(f"  ❌ Nomes problemáticos: {nomes_problematicos}")
            
            if nomes_problematicos == 0:
                print()
                print("🎉 CORREÇÃO APLICADA COM SUCESSO!")
                print("✅ Todos os produtos agora têm nomes válidos!")
            else:
                print()
                print("⚠️  Ainda existem alguns produtos com nomes problemáticos")
        
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
        
        print()
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ ERRO durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    testar_endpoint_corrigido()
