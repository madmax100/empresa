#!/usr/bin/env python
"""
Script para verificar as datas das movimentações importadas
"""

import os
import sys
import django

# Configurar o ambiente Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import MovimentacoesEstoque

def verificar_datas():
    """Verifica uma amostra das datas importadas"""
    
    # Verificar primeiros 10 registros
    print("=== AMOSTRA DAS DATAS IMPORTADAS ===")
    movimentacoes = MovimentacoesEstoque.objects.all()[:10]
    
    for mov in movimentacoes:
        print(f"ID: {mov.id}")
        print(f"Produto: {mov.produto.codigo if mov.produto else 'N/A'}")
        print(f"Data Movimentação: {mov.data_movimentacao}")
        print(f"Data Cadastro: {mov.data_cadastro}")
        print(f"Quantidade: {mov.quantidade}")
        print(f"Documento: {mov.documento_referencia}")
        print("-" * 50)
    
    # Estatísticas de datas
    print("\n=== ESTATÍSTICAS DE DATAS ===")
    total = MovimentacoesEstoque.objects.count()
    print(f"Total de registros: {total}")
    
    # Agrupar por ano
    from django.db.models import Count
    from django.db.models.functions import Extract
    
    anos = MovimentacoesEstoque.objects.annotate(
        ano=Extract('data_movimentacao', 'year')
    ).values('ano').annotate(
        total=Count('id')
    ).order_by('ano')
    
    print("\nDistribuição por ano:")
    for ano in anos:
        print(f"  {ano['ano']}: {ano['total']} registros")

if __name__ == "__main__":
    verificar_datas()
