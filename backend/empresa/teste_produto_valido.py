#!/usr/bin/env python
"""
Teste rápido para encontrar produtos válidos no estoque
"""
import os
import sys
import django
import requests

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

def encontrar_produto_valido():
    """Encontra um produto válido no estoque para teste"""
    
    print("Buscando produto válido no estoque...")
    
    # Testa endpoint com limite 5 para ver produtos válidos
    url = "http://127.0.0.1:8000/api/estoque-controle/estoque_atual/?limite=5"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            produtos = data.get('estoque', [])
            
            if produtos:
                print("\n✅ Produtos encontrados no estoque:")
                for i, produto in enumerate(produtos[:3], 1):
                    produto_id = produto.get('produto_id')
                    nome = produto.get('nome', 'N/A')
                    quantidade = produto.get('quantidade_atual', 0)
                    print(f"   {i}. ID: {produto_id} - {nome} - Qty: {quantidade}")
                
                # Usa o primeiro produto para um teste específico
                primeiro_produto_id = produtos[0].get('produto_id')
                print(f"\n🔍 Testando produto específico ID: {primeiro_produto_id}")
                
                # Testa endpoint com produto específico
                url_produto = f"http://127.0.0.1:8000/api/estoque-controle/estoque_atual/?produto_id={primeiro_produto_id}"
                
                response_produto = requests.get(url_produto, timeout=10)
                
                if response_produto.status_code == 200:
                    data_produto = response_produto.json()
                    produto_detalhes = data_produto.get('estoque', [])
                    
                    if produto_detalhes:
                        p = produto_detalhes[0]
                        print(f"✅ Teste de produto específico SUCESSO!")
                        print(f"   Nome: {p.get('nome', 'N/A')}")
                        print(f"   Quantidade: {p.get('quantidade_atual', 0)}")
                        print(f"   Valor: R$ {p.get('valor_atual', 0):,.2f}")
                        print(f"   Movimentações: {p.get('total_movimentacoes', 0)}")
                    else:
                        print("❌ Produto específico retornou sem dados")
                else:
                    print(f"❌ Erro ao buscar produto específico: {response_produto.status_code}")
                    try:
                        error_data = response_produto.json()
                        print(f"   Erro: {error_data.get('error', 'N/A')}")
                    except:
                        pass
                
                return primeiro_produto_id
            else:
                print("❌ Nenhum produto encontrado no estoque")
                return None
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return None

if __name__ == "__main__":
    encontrar_produto_valido()
