#!/usr/bin/env python3
"""
Teste do cálculo retroativo de estoque
"""

import os
import sys
import django
from datetime import datetime, date

# Configurar Django
sys.path.append('backend/empresa')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import Produtos, MovimentacoesEstoque
from contas.services.stock_calculation_service import StockCalculationService

def testar_calculo_retroativo():
    print("=== TESTE DO CÁLCULO RETROATIVO ===\n")
    
    # Produto 2867 - que tem muitas movimentações
    produto_id = 2867
    produto = Produtos.objects.get(id=produto_id)
    
    print(f"Produto: {produto.codigo} - {produto.nome}")
    print(f"Estoque Atual: {produto.estoque_atual}")
    
    # Testar algumas datas
    datas_teste = [
        date(2025, 9, 15),  # Hoje
        date(2025, 9, 1),   # Início do mês
        date(2025, 8, 1),   # Mês passado
        date(2025, 1, 1),   # Início do ano
        date(2024, 12, 31), # Final do ano passado
    ]
    
    print("\nTestes de cálculo por data:")
    print("-" * 50)
    
    for data_teste in datas_teste:
        estoque_calculado = StockCalculationService.calculate_stock_at_date(produto_id, data_teste)
        print(f"{data_teste.strftime('%Y-%m-%d')}: {estoque_calculado}")
    
    # Verificar se há movimentações recentes para validar
    print(f"\n=== MOVIMENTAÇÕES RECENTES ===")
    
    movs_recentes = MovimentacoesEstoque.objects.filter(
        produto_id=produto_id,
        data_movimentacao__gte=date(2025, 8, 1)
    ).order_by('-data_movimentacao')[:10]
    
    print("Últimas 10 movimentações desde agosto/2025:")
    for mov in movs_recentes:
        tipo_desc = mov.tipo_movimentacao.descricao if mov.tipo_movimentacao else 'N/A'
        print(f"{mov.data_movimentacao.strftime('%Y-%m-%d')}: {tipo_desc} {mov.quantidade}")

if __name__ == "__main__":
    testar_calculo_retroativo()