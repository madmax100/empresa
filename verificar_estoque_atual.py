#!/usr/bin/env python3
"""
Script para verificar o estoque atual dos produtos e como está sendo calculado
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

def verificar_estoque():
    print("=== VERIFICAÇÃO DE ESTOQUE ATUAL ===\n")
    
    # Pegar alguns produtos com estoque
    produtos_com_estoque = Produtos.objects.filter(
        estoque_atual__gt=0,
        ativo=True
    ).order_by('-estoque_atual')[:10]
    
    print("Top 10 produtos com maior estoque_atual:")
    print("-" * 80)
    print(f"{'ID':<5} {'Código':<10} {'Nome':<30} {'Estoque Atual':<15} {'Calc. Hoje':<15}")
    print("-" * 80)
    
    for produto in produtos_com_estoque:
        try:
            calc_hoje = StockCalculationService.calculate_stock_at_date(produto.id, date.today())
            diferenca = float(produto.estoque_atual or 0) - float(calc_hoje)
            
            print(f"{produto.id:<5} {produto.codigo:<10} {produto.nome[:28]:<30} "
                  f"{produto.estoque_atual:<15} {calc_hoje:<15} (Dif: {diferenca:.2f})")
        except Exception as e:
            print(f"{produto.id:<5} {produto.codigo:<10} {produto.nome[:28]:<30} "
                  f"{produto.estoque_atual:<15} ERRO: {str(e):<15}")
    
    print("\n=== VERIFICAÇÃO DE MOVIMENTAÇÕES ===\n")
    
    # Verificar algumas movimentações recentes
    movimentacoes_recentes = MovimentacoesEstoque.objects.all().order_by('-data_movimentacao')[:5]
    
    print("Últimas 5 movimentações:")
    print("-" * 100)
    print(f"{'Produto ID':<10} {'Data':<12} {'Tipo':<15} {'Qtd':<10} {'Doc':<15}")
    print("-" * 100)
    
    for mov in movimentacoes_recentes:
        print(f"{mov.produto_id:<10} {mov.data_movimentacao.strftime('%Y-%m-%d'):<12} "
              f"{mov.tipo_movimentacao.descricao if mov.tipo_movimentacao else 'N/A':<15} "
              f"{mov.quantidade:<10} {mov.documento_referencia:<15}")
    
    print("\n=== RESETS DE ESTOQUE (000000) ===\n")
    
    # Verificar se há resets de estoque
    resets = MovimentacoesEstoque.objects.filter(documento_referencia='000000').count()
    print(f"Total de resets de estoque encontrados: {resets}")
    
    if resets > 0:
        alguns_resets = MovimentacoesEstoque.objects.filter(
            documento_referencia='000000'
        ).order_by('-data_movimentacao')[:5]
        
        print("\nÚltimos 5 resets:")
        print("-" * 80)
        for reset in alguns_resets:
            print(f"Produto {reset.produto_id}: {reset.quantidade} em {reset.data_movimentacao.strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    verificar_estoque()