#!/usr/bin/env python
"""
Script para buscar produtos com movimentações
"""
import os
import sys
import django

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from contas.models import MovimentacoesEstoque, Produtos
from django.db.models import Count, Min, Max

def buscar_produtos_com_movimentacoes():
    print('=' * 60)
    print('BUSCANDO PRODUTOS COM MOVIMENTAÇÕES')
    print('=' * 60)
    
    # Busca produtos com mais movimentações
    produtos_com_movs = MovimentacoesEstoque.objects.values('produto_id').annotate(
        total_movs=Count('id')
    ).order_by('-total_movs')[:10]
    
    print('Top 10 produtos com mais movimentações:')
    print()
    
    for i, item in enumerate(produtos_com_movs, 1):
        produto_id = item['produto_id']
        total_movs = item['total_movs']
        
        try:
            produto = Produtos.objects.get(id=produto_id)
            nome = produto.nome or f'Produto {produto_id}'
        except:
            nome = f'Produto {produto_id}'
        
        print(f'{i:2d}. ID: {produto_id:4d} - {nome:<50} - {total_movs:3d} movimentações')
    
    print()
    print('=' * 60)
    print('VERIFICANDO DATAS DAS MOVIMENTAÇÕES')
    print('=' * 60)
    
    # Verifica as datas das movimentações
    datas = MovimentacoesEstoque.objects.aggregate(
        data_min=Min('data_movimentacao'),
        data_max=Max('data_movimentacao')
    )
    
    print(f'Data mais antiga: {datas["data_min"]}')
    print(f'Data mais recente: {datas["data_max"]}')
    
    # Total de movimentações
    total_movs = MovimentacoesEstoque.objects.count()
    print(f'Total de movimentações: {total_movs}')
    
    # Movimentações por mês
    print()
    print('Movimentações por período:')
    
    # 2025-01
    movs_jan = MovimentacoesEstoque.objects.filter(data_movimentacao__year=2025, data_movimentacao__month=1).count()
    print(f'Janeiro 2025: {movs_jan} movimentações')
    
    # 2025-02
    movs_fev = MovimentacoesEstoque.objects.filter(data_movimentacao__year=2025, data_movimentacao__month=2).count()
    print(f'Fevereiro 2025: {movs_fev} movimentações')
    
    # 2025-03
    movs_mar = MovimentacoesEstoque.objects.filter(data_movimentacao__year=2025, data_movimentacao__month=3).count()
    print(f'Março 2025: {movs_mar} movimentações')
    
    # Seleciona o produto com mais movimentações para teste
    if produtos_com_movs:
        produto_teste = produtos_com_movs[0]
        produto_id_teste = produto_teste['produto_id']
        total_movs_teste = produto_teste['total_movs']
        
        print()
        print('=' * 60)
        print(f'PRODUTO SELECIONADO PARA TESTE: ID {produto_id_teste}')
        print('=' * 60)
        
        # Busca movimentações deste produto específico por data
        movs_produto = MovimentacoesEstoque.objects.filter(produto_id=produto_id_teste).order_by('data_movimentacao')
        
        print(f'Total de movimentações do produto: {movs_produto.count()}')
        
        if movs_produto.exists():
            primeira_mov = movs_produto.first()
            ultima_mov = movs_produto.last()
            
            print(f'Primeira movimentação: {primeira_mov.data_movimentacao}')
            print(f'Última movimentação: {ultima_mov.data_movimentacao}')
            
            print()
            print('Primeiras 5 movimentações:')
            for i, mov in enumerate(movs_produto[:5], 1):
                tipo_nome = str(mov.tipo_movimentacao) if mov.tipo_movimentacao else 'N/A'
                print(f'{i}. {mov.data_movimentacao} - {tipo_nome} - Qty: {mov.quantidade} - Valor: R$ {mov.valor_total or 0:.2f}')
        
        return produto_id_teste
    
    return None

if __name__ == "__main__":
    produto_teste = buscar_produtos_com_movimentacoes()
    if produto_teste:
        print(f'\n🎯 Use o produto ID {produto_teste} para os testes de variação por data!')
    else:
        print('\n❌ Nenhum produto com movimentações encontrado!')
