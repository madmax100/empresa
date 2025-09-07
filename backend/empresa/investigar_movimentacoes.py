#!/usr/bin/env python
"""
Script para investigar movimentações do produto 3391
"""
import os
import sys
import django

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from contas.models import MovimentacoesEstoque

def investigar_movimentacoes():
    print('=' * 60)
    print('MOVIMENTAÇÕES DETALHADAS DO PRODUTO 3391')
    print('=' * 60)
    
    movs = MovimentacoesEstoque.objects.filter(produto_id=3391).order_by('data_movimentacao')
    
    print(f'Total de movimentações: {movs.count()}')
    print()
    
    for i, mov in enumerate(movs, 1):
        print(f'{i}. Data: {mov.data_movimentacao}')
        print(f'   Tipo: {mov.tipo_movimentacao}')
        print(f'   Quantidade: {mov.quantidade}')
        print(f'   Valor unitário: {mov.custo_unitario or "N/A"}')
        print(f'   Valor total: {mov.valor_total or "N/A"}')
        print(f'   Observações: {mov.observacoes or "N/A"}')
        print()

if __name__ == "__main__":
    investigar_movimentacoes()
