#!/usr/bin/env python
"""
Script to check current stock values using the new StockCalculationService
"""
import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import Produtos, MovimentacoesEstoque
from contas.services.stock_calculation import StockCalculationService
from contas.services.stock_validation import StockValidationService

def show_current_stock():
    """Display current stock information"""
    print("=" * 80)
    print("CURRENT STOCK ANALYSIS")
    print("=" * 80)
    
    # Get some products to analyze
    produtos = Produtos.objects.filter(ativo=True)[:10]  # First 10 active products
    
    if not produtos.exists():
        print("No active products found in the database.")
        return
    
    print(f"\nAnalyzing {produtos.count()} products:\n")
    print(f"{'Code':<15} {'Name':<30} {'Stored':<10} {'Calculated':<12} {'Difference':<12} {'Status'}")
    print("-" * 95)
    
    total_products = 0
    correct_count = 0
    discrepancies = []
    
    for produto in produtos:
        try:
            # Get stored stock from database
            stored_stock = Decimal(str(produto.estoque_atual or 0))
            
            # Calculate current stock using our service
            calculated_stock = StockCalculationService.calculate_current_stock(produto.id)
            
            # Calculate difference
            difference = calculated_stock - stored_stock
            status = "✓ OK" if difference == 0 else "✗ DIFF"
            
            if difference == 0:
                correct_count += 1
            else:
                discrepancies.append({
                    'codigo': produto.codigo,
                    'nome': produto.nome,
                    'stored': stored_stock,
                    'calculated': calculated_stock,
                    'difference': difference
                })
            
            print(f"{produto.codigo:<15} {produto.nome[:28]:<30} {stored_stock:<10} {calculated_stock:<12} {difference:<12} {status}")
            total_products += 1
            
        except Exception as e:
            print(f"{produto.codigo:<15} {produto.nome[:28]:<30} {'ERROR':<10} {'ERROR':<12} {'ERROR':<12} ✗ ERR")
            print(f"  Error: {str(e)}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total products analyzed: {total_products}")
    print(f"Correct stock values: {correct_count}")
    print(f"Stock discrepancies: {len(discrepancies)}")
    
    if total_products > 0:
        accuracy = (correct_count / total_products) * 100
        print(f"Accuracy: {accuracy:.1f}%")
    
    # Show largest discrepancies
    if discrepancies:
        print(f"\nLargest discrepancies:")
        discrepancies.sort(key=lambda x: abs(x['difference']), reverse=True)
        for i, disc in enumerate(discrepancies[:5], 1):
            print(f"{i}. {disc['codigo']} - {disc['nome'][:25]}")
            print(f"   Stored: {disc['stored']}, Calculated: {disc['calculated']}, Diff: {disc['difference']}")

def show_stock_movements_sample():
    """Show sample stock movements"""
    print("\n" + "=" * 80)
    print("RECENT STOCK MOVEMENTS (Sample)")
    print("=" * 80)
    
    # Get recent movements
    recent_movements = MovimentacoesEstoque.objects.select_related(
        'produto', 'tipo_movimentacao'
    ).order_by('-data_movimentacao')[:10]
    
    if not recent_movements.exists():
        print("No stock movements found.")
        return
    
    print(f"{'Date':<12} {'Product':<15} {'Type':<10} {'Qty':<10} {'Doc':<15}")
    print("-" * 70)
    
    for mov in recent_movements:
        date_str = mov.data_movimentacao.strftime('%Y-%m-%d')
        product_code = mov.produto.codigo if mov.produto else 'N/A'
        mov_type = mov.tipo_movimentacao.tipo if mov.tipo_movimentacao else 'N/A'
        quantity = mov.quantidade
        doc_ref = mov.documento_referencia or 'N/A'
        
        print(f"{date_str:<12} {product_code:<15} {mov_type:<10} {quantity:<10} {doc_ref:<15}")

def show_validation_report():
    """Show a validation report"""
    print("\n" + "=" * 80)
    print("STOCK VALIDATION REPORT")
    print("=" * 80)
    
    try:
        # Run validation on first 5 products
        produtos = Produtos.objects.filter(ativo=True)[:5]
        produto_ids = [p.id for p in produtos]
        
        if not produto_ids:
            print("No products to validate.")
            return
        
        report = StockValidationService.generate_validation_report(produto_ids)
        
        print(f"Products validated: {report['total_products']}")
        print(f"Correct stock: {report['correct_stock']}")
        print(f"Incorrect stock: {report['incorrect_stock']}")
        print(f"Accuracy: {report['summary']['accuracy_percentage']:.1f}%")
        
        if report['discrepancies']:
            print(f"\nDiscrepancies found: {len(report['discrepancies'])}")
            for disc in report['discrepancies'][:3]:  # Show first 3
                print(f"- {disc['produto_codigo']}: Stored={disc['stored_stock']}, Calculated={disc['calculated_stock']}")
        
        if report['recommendations']:
            print(f"\nRecommendations:")
            for rec in report['recommendations']:
                print(f"- {rec}")
                
    except Exception as e:
        print(f"Error generating validation report: {str(e)}")

if __name__ == "__main__":
    try:
        show_current_stock()
        show_stock_movements_sample()
        show_validation_report()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)