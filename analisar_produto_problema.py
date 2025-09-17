#!/usr/bin/env python3
"""
Script para analisar um produto específico que tem diferença entre estoque_atual e calculado
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

def analisar_produto_2867():
    """Analisar produto 2867 que tem 29 no estoque_atual mas 12 no calculado"""
    
    produto_id = 2867
    
    print(f"=== ANÁLISE DETALHADA DO PRODUTO {produto_id} ===\n")
    
    # Informações do produto
    produto = Produtos.objects.get(id=produto_id)
    print(f"Produto: {produto.codigo} - {produto.nome}")
    print(f"Estoque Atual (importado): {produto.estoque_atual}")
    
    # Calcular estoque para hoje
    calc_hoje = StockCalculationService.calculate_stock_at_date(produto_id, date.today())
    print(f"Estoque Calculado (hoje): {calc_hoje}")
    print(f"Diferença: {float(produto.estoque_atual or 0) - float(calc_hoje)}")
    
    print("\n=== MOVIMENTAÇÕES DO PRODUTO ===\n")
    
    # Todas as movimentações do produto
    movimentacoes = MovimentacoesEstoque.objects.filter(
        produto_id=produto_id
    ).order_by('data_movimentacao')
    
    print(f"Total de movimentações: {movimentacoes.count()}")
    print("-" * 100)
    print(f"{'Data':<12} {'Tipo':<15} {'Qtd':<10} {'Doc':<15} {'Observação':<30}")
    print("-" * 100)
    
    for mov in movimentacoes:
        tipo_desc = mov.tipo_movimentacao.descricao if mov.tipo_movimentacao else 'N/A'
        print(f"{mov.data_movimentacao.strftime('%Y-%m-%d'):<12} "
              f"{tipo_desc:<15} "
              f"{mov.quantidade:<10} "
              f"{mov.documento_referencia:<15} "
              f"{(mov.observacoes or '')[:28]:<30}")
    
    print("\n=== ANÁLISE DE RESETS ===\n")
    
    # Verificar se há resets para este produto
    resets = MovimentacoesEstoque.objects.filter(
        produto_id=produto_id,
        documento_referencia='000000'
    ).order_by('-data_movimentacao')
    
    print(f"Resets encontrados: {resets.count()}")
    for reset in resets:
        print(f"Reset em {reset.data_movimentacao.strftime('%Y-%m-%d')}: {reset.quantidade}")
    
    print("\n=== SIMULAÇÃO DO CÁLCULO CORRETO ===\n")
    
    # Como deveria ser o cálculo correto:
    # Estoque inicial = estoque_atual (29)
    # Para data hoje = estoque_inicial - movimentações posteriores
    # Para datas passadas = estoque_inicial - movimentações posteriores à data
    
    print("LÓGICA CORRETA:")
    print(f"1. Estoque inicial (importado): {produto.estoque_atual}")
    print("2. Para calcular estoque em uma data passada:")
    print("   Estoque = estoque_inicial - movimentações_após_data")
    print("3. Para calcular estoque hoje:")
    print("   Estoque = estoque_inicial (sem ajustes se não há movimentações após hoje)")

if __name__ == "__main__":
    analisar_produto_2867()