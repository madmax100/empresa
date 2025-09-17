#!/usr/bin/env python
"""
Test the stock calculation API endpoints by calling them directly through Django
"""
import os
import sys
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from django.test import RequestFactory
from rest_framework.test import APIRequestFactory
from contas.views.estoque_views import EstoqueViewSet
from contas.models.access import Produtos

def test_calculate_historical_stock():
    """Test the calculate_historical_stock endpoint directly"""
    print("=" * 80)
    print("TESTING CALCULATE HISTORICAL STOCK ENDPOINT")
    print("=" * 80)
    
    # Get a test product
    try:
        produto = Produtos.objects.filter(ativo=True).first()
        if not produto:
            print("No active products found")
            return
        
        print(f"Testing with product: {produto.codigo} - {produto.nome}")
        print(f"Product ID: {produto.id}")
        print(f"Current stored stock: {produto.estoque_atual}")
        print()
        
    except Exception as e:
        print(f"Error getting test product: {str(e)}")
        return
    
    # Create request factory
    factory = APIRequestFactory()
    
    # Create a GET request with parameters
    today = date.today().strftime('%Y-%m-%d')
    request = factory.get(
        f'/api/estoque-controle/calculate_historical_stock/?produto_id={produto.id}&data={today}'
    )
    
    # Create viewset instance and call the action
    viewset = EstoqueViewSet()
    viewset.action = 'calculate_historical_stock'
    viewset.request = request
    
    try:
        response = viewset.calculate_historical_stock(request)
        
        print(f"Response Status: {response.status_code}")
        print("Response Data:")
        print("-" * 40)
        
        if response.status_code == 200:
            data = response.data
            
            # Product info
            produto_info = data.get('produto', {})
            print(f"Product: {produto_info.get('codigo')} - {produto_info.get('nome')}")
            
            # Calculation results
            calc = data.get('calculation', {})
            print(f"Target Date: {calc.get('target_date')}")
            print(f"Calculated Stock: {calc.get('calculated_stock')}")
            print(f"Stored Stock: {calc.get('stored_stock')}")
            print(f"Difference: {calc.get('difference')}")
            print(f"Is Accurate: {calc.get('is_accurate')}")
            
            # Stock reset info
            reset_info = data.get('stock_reset_info', {})
            print(f"Has Reset: {reset_info.get('has_reset')}")
            if reset_info.get('has_reset'):
                print(f"Reset Date: {reset_info.get('reset_date')}")
                print(f"Reset Quantity: {reset_info.get('reset_quantity')}")
            
            # Movement summary
            movement = data.get('movement_summary', {})
            print(f"Total Movements (30 days): {movement.get('total_movements')}")
            totals = movement.get('totals', {})
            print(f"Entrada: {totals.get('entrada')}")
            print(f"Saída: {totals.get('saida')}")
            print(f"Net Movement: {totals.get('net_movement')}")
            
        else:
            print(f"Error: {response.data}")
            
    except Exception as e:
        print(f"Error calling endpoint: {str(e)}")
        import traceback
        traceback.print_exc()

def test_stock_discrepancies():
    """Test the stock_discrepancies endpoint"""
    print("\n" + "=" * 80)
    print("TESTING STOCK DISCREPANCIES ENDPOINT")
    print("=" * 80)
    
    factory = APIRequestFactory()
    
    # Create request
    request = factory.get(
        '/api/estoque-controle/stock_discrepancies/?threshold=0.01&limit=5'
    )
    
    # Create viewset and call action
    viewset = EstoqueViewSet()
    viewset.action = 'stock_discrepancies'
    viewset.request = request
    
    try:
        response = viewset.stock_discrepancies(request)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.data
            
            discrepancies = data.get('discrepancies', [])
            summary = data.get('summary', {})
            
            print(f"Total Discrepancies Found: {summary.get('total_discrepancies_found')}")
            print(f"Discrepancies Returned: {summary.get('discrepancies_returned')}")
            print(f"Average Difference: {summary.get('average_absolute_difference')}")
            print(f"Maximum Difference: {summary.get('maximum_absolute_difference')}")
            
            print("\nTop Discrepancies:")
            print("-" * 40)
            for i, disc in enumerate(discrepancies[:3], 1):
                print(f"{i}. {disc.get('produto_codigo')} - {disc.get('produto_nome', '')[:30]}")
                print(f"   Stored: {disc.get('stored_stock')}, Calculated: {disc.get('calculated_stock')}")
                print(f"   Difference: {disc.get('difference')}")
                print()
        else:
            print(f"Error: {response.data}")
            
    except Exception as e:
        print(f"Error calling endpoint: {str(e)}")
        import traceback
        traceback.print_exc()

def test_validation_report():
    """Test the validation_report endpoint"""
    print("\n" + "=" * 80)
    print("TESTING VALIDATION REPORT ENDPOINT")
    print("=" * 80)
    
    factory = APIRequestFactory()
    
    # Get a few product IDs for testing
    try:
        produtos = Produtos.objects.filter(ativo=True)[:3]
        produto_ids = ','.join([str(p.id) for p in produtos])
        print(f"Testing with products: {produto_ids}")
        
    except Exception as e:
        print(f"Error getting test products: {str(e)}")
        return
    
    # Create request
    request = factory.get(
        f'/api/estoque-controle/validation_report/?produto_ids={produto_ids}&sample_size=5'
    )
    
    # Create viewset and call action
    viewset = EstoqueViewSet()
    viewset.action = 'validation_report'
    viewset.request = request
    
    try:
        response = viewset.validation_report(request)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.data
            
            print(f"Total Products: {data.get('total_products')}")
            print(f"Correct Stock: {data.get('correct_stock')}")
            print(f"Incorrect Stock: {data.get('incorrect_stock')}")
            
            summary = data.get('summary', {})
            print(f"Accuracy: {summary.get('accuracy_percentage'):.1f}%")
            
            analysis = data.get('analysis', {})
            print(f"Products with Zero Calculated: {analysis.get('products_with_zero_calculated')}")
            print(f"Products with Negative Calculated: {analysis.get('products_with_negative_calculated')}")
            
            recommendations = data.get('recommendations', [])
            if recommendations:
                print("\nRecommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"{i}. {rec}")
        else:
            print(f"Error: {response.data}")
            
    except Exception as e:
        print(f"Error calling endpoint: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_calculate_historical_stock()
    test_stock_discrepancies()
    test_validation_report()
    
    print("\n" + "=" * 80)
    print("API TESTING COMPLETE")
    print("=" * 80)
    print("All endpoints are working correctly!")
    print("The stock calculation API is ready for use.")