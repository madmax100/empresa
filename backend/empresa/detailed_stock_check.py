#!/usr/bin/env python
"""
Detailed stock analysis for specific products
"""
import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import Produtos, MovimentacoesEstoque, TiposMovimentacaoEstoque
from contas.services.stock_calculation import StockCalculationService
from contas.services.stock_validation import StockValidationService

def analyze_specific_product(produto_codigo):
    """Analyze a specific product in detail"""
    try:
        produto = Produtos.objects.get(codigo=produto_codigo)
    except Produtos.DoesNotExist:
        print(f"Product with code '{produto_codigo}' not found.")
        return
    
    print("=" * 80)
    print(f"DETAILED ANALYSIS: {produto.codigo} - {produto.nome}")
    print("=" * 80)
    
    # Basic info
    print(f"Product ID: {produto.id}")
    print(f"Active: {produto.ativo}")
    print(f"Stored Stock (estoque_atual): {produto.estoque_atual}")
    
    # Calculate current stock
    try:
        calculated_stock = StockCalculationService.calculate_current_stock(produto.id)
        print(f"Calculated Current Stock: {calculated_stock}")
        
        difference = calculated_stock - Decimal(str(produto.estoque_atual))
        print(f"Difference: {difference}")
        print(f"Status: {'✓ CORRECT' if difference == 0 else '✗ DISCREPANCY'}")
        
    except Exception as e:
        print(f"Error calculating stock: {str(e)}")
        return
    
    # Show recent movements
    print(f"\nRECENT MOVEMENTS:")
    print("-" * 80)
    
    movements = MovimentacoesEstoque.objects.filter(
        produto=produto
    ).select_related('tipo_movimentacao').order_by('-data_movimentacao')[:10]
    
    if movements.exists():
        print(f"{'Date':<12} {'Type':<15} {'Qty':<10} {'Doc Ref':<15} {'Description'}")
        print("-" * 70)
        
        for mov in movements:
            date_str = mov.data_movimentacao.strftime('%Y-%m-%d')
            mov_type = mov.tipo_movimentacao.descricao if mov.tipo_movimentacao else 'N/A'
            tipo_letra = mov.tipo_movimentacao.tipo if mov.tipo_movimentacao else 'N/A'
            quantity = mov.quantidade
            doc_ref = mov.documento_referencia or 'N/A'
            
            # Special handling for resets
            if doc_ref == '000000':
                mov_type = "STOCK RESET"
            
            print(f"{date_str:<12} {tipo_letra:<3} {mov_type[:11]:<12} {quantity:<10} {doc_ref:<15}")
    else:
        print("No movements found for this product.")
    
    # Check for stock resets
    print(f"\nSTOCK RESET ANALYSIS:")
    print("-" * 80)
    
    resets = MovimentacoesEstoque.objects.filter(
        produto=produto,
        documento_referencia='000000'
    ).order_by('-data_movimentacao')
    
    if resets.exists():
        print(f"Found {resets.count()} stock reset(s):")
        for reset in resets:
            date_str = reset.data_movimentacao.strftime('%Y-%m-%d %H:%M')
            print(f"- {date_str}: Reset to {reset.quantidade}")
    else:
        print("No stock resets found (no '000000' movements).")
    
    # Validation details
    print(f"\nVALIDATION DETAILS:")
    print("-" * 80)
    
    try:
        validation = StockValidationService.validate_single_product(produto.id)
        
        print(f"Calculated Stock: {validation['calculated_stock']}")
        print(f"Stored Stock: {validation['stored_stock']}")
        print(f"Difference: {validation['difference']}")
        print(f"Is Correct: {validation['is_correct']}")
        
        reset_info = validation['stock_reset_info']
        print(f"Has Reset: {reset_info['has_reset']}")
        if reset_info['has_reset']:
            print(f"Reset Date: {reset_info['reset_date']}")
            print(f"Reset Quantity: {reset_info['reset_quantity']}")
        
        movement_info = validation['movement_info']
        print(f"Total Movements: {movement_info['total_movements']}")
        print(f"Regular Movements: {movement_info['regular_movements']}")
        print(f"Reset Movements: {movement_info['total_movements'] - movement_info['regular_movements']}")
        
    except Exception as e:
        print(f"Error in validation: {str(e)}")

def show_products_with_discrepancies():
    """Show products that have stock discrepancies"""
    print("=" * 80)
    print("PRODUCTS WITH STOCK DISCREPANCIES")
    print("=" * 80)
    
    try:
        discrepancies = StockValidationService.find_stock_discrepancies(Decimal('0.01'))
        
        if not discrepancies:
            print("No stock discrepancies found!")
            return
        
        print(f"Found {len(discrepancies)} products with discrepancies:\n")
        print(f"{'Code':<15} {'Name':<30} {'Stored':<10} {'Calculated':<12} {'Difference':<12}")
        print("-" * 85)
        
        for disc in discrepancies[:10]:  # Show first 10
            if disc.get('error'):
                print(f"{disc['produto_codigo']:<15} {disc['produto_nome'][:28]:<30} {'ERROR':<10} {'ERROR':<12} {'ERROR':<12}")
            else:
                print(f"{disc['produto_codigo']:<15} {disc['produto_nome'][:28]:<30} {disc['stored_stock']:<10} {disc['calculated_stock']:<12} {disc['difference']:<12}")
        
        if len(discrepancies) > 10:
            print(f"\n... and {len(discrepancies) - 10} more products with discrepancies.")
            
    except Exception as e:
        print(f"Error finding discrepancies: {str(e)}")

def show_database_stats():
    """Show general database statistics"""
    print("=" * 80)
    print("DATABASE STATISTICS")
    print("=" * 80)
    
    # Product stats
    total_products = Produtos.objects.count()
    active_products = Produtos.objects.filter(ativo=True).count()
    print(f"Total Products: {total_products}")
    print(f"Active Products: {active_products}")
    
    # Movement stats
    total_movements = MovimentacoesEstoque.objects.count()
    reset_movements = MovimentacoesEstoque.objects.filter(documento_referencia='000000').count()
    print(f"Total Stock Movements: {total_movements}")
    print(f"Stock Reset Movements: {reset_movements}")
    print(f"Regular Movements: {total_movements - reset_movements}")
    
    # Movement types
    movement_types = TiposMovimentacaoEstoque.objects.filter(ativo=True)
    print(f"Active Movement Types: {movement_types.count()}")
    for mt in movement_types:
        count = MovimentacoesEstoque.objects.filter(tipo_movimentacao=mt).count()
        print(f"  - {mt.codigo} ({mt.tipo}): {count} movements")

if __name__ == "__main__":
    # Show general stats first
    show_database_stats()
    
    # Show products with discrepancies
    show_products_with_discrepancies()
    
    # If a specific product code is provided, analyze it
    if len(sys.argv) > 1:
        produto_codigo = sys.argv[1]
        analyze_specific_product(produto_codigo)
    else:
        print("\n" + "=" * 80)
        print("To analyze a specific product, run:")
        print("python detailed_stock_check.py <product_code>")
        print("=" * 80)