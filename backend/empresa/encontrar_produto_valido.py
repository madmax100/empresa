#!/usr/bin/env python
"""
Script para encontrar produtos que estão no estoque inicial E têm movimentações
"""
import os
import sys
import django

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from contas.models import MovimentacoesEstoque, Produtos
from django.db.models import Count

def encontrar_produtos_estoque_inicial_com_movimentacoes():
    print('=' * 80)
    print('BUSCANDO PRODUTOS NO ESTOQUE INICIAL COM MOVIMENTAÇÕES')
    print('=' * 80)
    
    # Carrega o estoque inicial (adaptado do controle_estoque_completo.py)
    print("1. Carregando estoque inicial...")
    
    # Documento EST_INICIAL_2025 (adaptando a lógica)
    estoque_inicial = {}
    
    try:
        # Busca todos os produtos que existem
        produtos = Produtos.objects.all()
        print(f"   Total de produtos no sistema: {produtos.count()}")
        
        # Para simplificar, vamos assumir que produtos com ID menor têm mais chance de ter estoque inicial
        # Vou testar alguns produtos específicos que sabemos que existem
        produtos_teste = [10, 69, 109, 200, 300, 500, 1000, 2000, 3000, 3998]
        
        print("\n2. Testando produtos conhecidos...")
        
        produtos_validos = []
        
        for produto_id in produtos_teste:
            try:
                produto = Produtos.objects.get(id=produto_id)
                print(f"   ✅ Produto {produto_id}: {produto.nome}")
                produtos_validos.append(produto_id)
            except:
                print(f"   ❌ Produto {produto_id}: não encontrado")
        
        print(f"\n3. Verificando movimentações dos produtos válidos...")
        
        produtos_com_movs = []
        
        for produto_id in produtos_validos:
            movs_count = MovimentacoesEstoque.objects.filter(produto_id=produto_id).count()
            if movs_count > 0:
                produto = Produtos.objects.get(id=produto_id)
                nome = produto.nome or f"Produto {produto_id}"
                print(f"   ✅ Produto {produto_id}: {nome} - {movs_count} movimentações")
                produtos_com_movs.append({
                    'id': produto_id,
                    'nome': nome,
                    'movimentacoes': movs_count
                })
            else:
                produto = Produtos.objects.get(id=produto_id)
                nome = produto.nome or f"Produto {produto_id}"
                print(f"   ⚪ Produto {produto_id}: {nome} - SEM movimentações")
        
        if produtos_com_movs:
            print(f"\n4. PRODUTOS CANDIDATOS PARA TESTE:")
            print("-" * 60)
            
            # Ordena por número de movimentações
            produtos_com_movs.sort(key=lambda x: x['movimentacoes'], reverse=True)
            
            for i, produto in enumerate(produtos_com_movs, 1):
                print(f"{i:2d}. ID {produto['id']:4d} - {produto['nome']:<50} - {produto['movimentacoes']:3d} movs")
            
            # Retorna o produto com mais movimentações
            melhor_produto = produtos_com_movs[0]
            print(f"\n🎯 MELHOR CANDIDATO: ID {melhor_produto['id']} com {melhor_produto['movimentacoes']} movimentações")
            
            return melhor_produto['id']
        else:
            print("\n❌ Nenhum produto com movimentações encontrado entre os candidatos")
            
            # Vamos buscar nos primeiros produtos do sistema
            print("\n5. Buscando nos primeiros produtos do sistema...")
            
            primeiros_produtos = Produtos.objects.all()[:50]  # Primeiros 50
            
            for produto in primeiros_produtos:
                movs_count = MovimentacoesEstoque.objects.filter(produto_id=produto.id).count()
                if movs_count > 0:
                    print(f"   ✅ ID {produto.id}: {produto.nome} - {movs_count} movimentações")
                    return produto.id
            
            print("   ❌ Nenhum produto com movimentações encontrado")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return None

if __name__ == "__main__":
    produto_teste = encontrar_produtos_estoque_inicial_com_movimentacoes()
    
    if produto_teste:
        print(f"\n" + "="*80)
        print(f"🚀 USE O PRODUTO ID {produto_teste} PARA O TESTE DE VARIAÇÃO POR DATA!")
        print("="*80)
    else:
        print(f"\n" + "="*80)
        print("❌ NENHUM PRODUTO ADEQUADO ENCONTRADO")
        print("="*80)
