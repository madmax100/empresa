#!/usr/bin/env python
"""
🌐 EXEMPLO REAL DE RETORNO DO ENDPOINT
"""
import requests
import json
from datetime import datetime

def testar_endpoint_real():
    """Faz requisição real ao endpoint e mostra o retorno"""
    print("=" * 80)
    print("🌐 EXEMPLO REAL DE RETORNO DO ENDPOINT")
    print("=" * 80)
    
    try:
        url = "http://localhost:8000/contas/relatorio-valor-estoque/"
        
        print(f"📡 Fazendo requisição para: {url}")
        print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Fazer requisição real
        response = requests.get(url, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            
            print("🎯 RETORNO REAL DO ENDPOINT:")
            print("=" * 80)
            
            # Mostrar JSON formatado
            json_formatado = json.dumps(data, indent=2, ensure_ascii=False)
            print(json_formatado)
            
            print("=" * 80)
            print()
            
            # Análise dos dados
            print("📊 ANÁLISE DOS DADOS RETORNADOS:")
            print(f"  📅 Data de posição: {data.get('data_posicao')}")
            print(f"  💰 Valor total: R$ {data.get('valor_total_estoque', 0):,.2f}")
            print(f"  📦 Total de produtos: {data.get('total_produtos_em_estoque', 0)}")
            
            produtos = data.get('detalhes_por_produto', [])
            print(f"  📋 Produtos retornados: {len(produtos)}")
            
            if produtos:
                print()
                print("🎯 PRIMEIROS 5 PRODUTOS (DADOS REAIS):")
                for i, produto in enumerate(produtos[:5]):
                    print(f"  {i+1}. ID: {produto.get('produto_id', 'N/A')}")
                    print(f"     📝 Nome: '{produto.get('produto_descricao', 'N/A')}'")
                    print(f"     📁 Categoria: '{produto.get('categoria', 'N/A')}'")
                    print(f"     📊 Quantidade: {produto.get('quantidade_em_estoque', 0)}")
                    print(f"     💵 Valor: R$ {produto.get('valor_total_produto', 0):,.2f}")
                    print()
                
                # Análise das categorias
                categorias = {}
                for produto in produtos:
                    cat = produto.get('categoria', 'Sem categoria')
                    categorias[cat] = categorias.get(cat, 0) + 1
                
                print("📁 DISTRIBUIÇÃO POR CATEGORIAS (DADOS REAIS):")
                for categoria, quantidade in sorted(categorias.items(), key=lambda x: x[1], reverse=True):
                    porcentagem = (quantidade / len(produtos)) * 100
                    print(f"  📁 {categoria}: {quantidade} produtos ({porcentagem:.1f}%)")
            
            print()
            print("✅ ENDPOINT FUNCIONANDO PERFEITAMENTE!")
            print("🎉 Dados reais retornados com sucesso!")
            
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Não foi possível conectar ao servidor")
        print("🔧 Verifique se o Django está rodando em http://localhost:8000")
        
    except Exception as e:
        print(f"❌ ERRO inesperado: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    testar_endpoint_real()
