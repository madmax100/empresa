#!/usr/bin/env python
"""
Test the refactored Historical Stock Analysis API
"""
import os
import sys
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import Produtos
from contas.views.estoque_views import EstoqueViewSet
import json

class MockRequest:
    """Mock request object with query_params"""
    def __init__(self, params):
        self.query_params = params
        self.method = 'GET'

def test_historical_api():
    """Test the refactored historical stock API"""
    
    print("=" * 80)
    print("TESTING REFACTORED HISTORICAL STOCK ANALYSIS API")
    print("=" * 80)
    
    # Get test products
    try:
        produtos_query = Produtos.objects.filter(ativo=True)
        if not produtos_query.exists():
            print("❌ No active products found for testing")
            return False
        
        produtos = list(produtos_query[:5])
        test_produto = produtos[0]
        produto_ids = [str(p.id) for p in produtos]
        
        print(f"✓ Using test product: {test_produto.codigo} - {test_produto.nome}")
        print(f"✓ Product ID: {test_produto.id}")
        print(f"✓ Current stock: {test_produto.estoque_atual}")
        print()
        
    except Exception as e:
        print(f"❌ Error getting test products: {str(e)}")
        return False
    
    # Create viewset instance
    viewset = EstoqueViewSet()
    
    # Test data
    today = date.today()
    yesterday = today - timedelta(days=1)
    last_month = today - timedelta(days=30)
    
    # Test cases for refactored API
    test_cases = [
        {
            'name': 'Calculate Historical Stock',
            'method': 'calculate_historical_stock',
            'params': {
                'produto_id': str(test_produto.id),
                'data': yesterday.strftime('%Y-%m-%d')
            }
        },
        {
            'name': 'Stock Movements Analysis',
            'method': 'stock_movements_analysis',
            'params': {
                'produto_ids': ','.join(produto_ids[:3]),
                'start_date': last_month.strftime('%Y-%m-%d'),
                'end_date': today.strftime('%Y-%m-%d'),
                'limit': '5'
            }
        },
        {
            'name': 'Stock Timeline (Weekly)',
            'method': 'stock_timeline',
            'params': {
                'produto_id': str(test_produto.id),
                'start_date': last_month.strftime('%Y-%m-%d'),
                'end_date': today.strftime('%Y-%m-%d'),
                'interval': 'weekly'
            }
        },
        {
            'name': 'Stock Resets Report',
            'method': 'stock_resets_report',
            'params': {
                'start_date': (today - timedelta(days=365)).strftime('%Y-%m-%d'),
                'limit': '10'
            }
        },
        {
            'name': 'Product Stock History',
            'method': 'product_stock_history',
            'params': {
                'produto_id': str(test_produto.id),
                'days_history': '90',
                'include_movements': 'true'
            }
        }
    ]
    
    # Run tests
    results = []
    for test_case in test_cases:
        print(f"Testing: {test_case['name']}")
        print(f"Method: {test_case['method']}")
        print(f"Params: {test_case['params']}")
        
        try:
            # Create mock request
            request = MockRequest(test_case['params'])
            
            # Get the method from viewset
            method = getattr(viewset, test_case['method'])
            
            # Call the method
            response = method(request)
            
            if response.status_code == 200:
                try:
                    data = response.data
                    print(f"✅ PASS - Status 200, valid response")
                    
                    # Show key information based on endpoint
                    if 'produto' in data and 'historical_calculation' in data:
                        produto_info = data['produto']
                        calc = data['historical_calculation']
                        print(f"   Product: {produto_info.get('codigo')} - {produto_info.get('nome', '')[:40]}")
                        print(f"   Historical Stock: {calc.get('historical_stock')}")
                        print(f"   Target Date: {calc.get('target_date')}")
                    
                    elif 'analysis_results' in data:
                        results_data = data['analysis_results']
                        summary = data.get('summary', {})
                        print(f"   Products Analyzed: {len(results_data)}")
                        print(f"   Period: {summary.get('period', {}).get('days_analyzed', 0)} days")
                        print(f"   Products with Movements: {summary.get('products_with_movements', 0)}")
                    
                    elif 'timeline' in data:
                        timeline = data['timeline']
                        stats = timeline.get('statistics', {})
                        print(f"   Timeline Points: {stats.get('total_points', 0)}")
                        print(f"   Stock Range: {stats.get('min_stock', 0)} - {stats.get('max_stock', 0)}")
                        print(f"   Average Stock: {stats.get('avg_stock', 0)}")
                    
                    elif 'reset_analysis' in data:
                        summary = data.get('summary', {})
                        print(f"   Total Resets: {summary.get('total_resets', 0)}")
                        print(f"   Products with Resets: {summary.get('products_with_resets', 0)}")
                        print(f"   Products Returned: {summary.get('products_returned', 0)}")
                    
                    elif 'stock_levels' in data:
                        levels = data['stock_levels']
                        print(f"   Stock at Period Start: {levels.get('stock_at_period_start', 0)}")
                        print(f"   Stock at Period End: {levels.get('stock_at_period_end', 0)}")
                        print(f"   Net Change: {levels.get('net_change_in_period', 0)}")
                    
                    results.append(True)
                    
                except Exception as e:
                    print(f"❌ FAIL - Error parsing response: {str(e)}")
                    results.append(False)
            else:
                print(f"❌ FAIL - Status {response.status_code}")
                try:
                    error_data = response.data
                    print(f"   Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"   Response: {str(response.data)[:200]}")
                results.append(False)
                
        except Exception as e:
            print(f"❌ FAIL - Exception: {str(e)}")
            results.append(False)
        
        print("-" * 60)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 80)
    print("REFACTORED API TEST SUMMARY")
    print("=" * 80)
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    return passed == total

def test_error_handling():
    """Test error handling for the refactored API"""
    print("\n" + "=" * 80)
    print("TESTING ERROR HANDLING")
    print("=" * 80)
    
    viewset = EstoqueViewSet()
    
    error_tests = [
        {
            'name': 'Future date not allowed',
            'method': 'calculate_historical_stock',
            'params': {'produto_id': '1', 'data': '2026-01-01'},
            'expected_status': 400
        },
        {
            'name': 'Missing required parameters',
            'method': 'stock_movements_analysis',
            'params': {'produto_ids': '1'},  # Missing start_date and end_date
            'expected_status': 400
        },
        {
            'name': 'Invalid interval',
            'method': 'stock_timeline',
            'params': {
                'produto_id': '1',
                'start_date': '2024-01-01',
                'end_date': '2024-01-31',
                'interval': 'invalid'
            },
            'expected_status': 400
        },
        {
            'name': 'Non-existent product',
            'method': 'product_stock_history',
            'params': {'produto_id': '999999'},
            'expected_status': 404
        }
    ]
    
    error_results = []
    for test in error_tests:
        print(f"Testing: {test['name']}")
        
        try:
            request = MockRequest(test['params'])
            method = getattr(viewset, test['method'])
            response = method(request)
            
            if response.status_code == test['expected_status']:
                print(f"✅ PASS - Got expected status {response.status_code}")
                try:
                    if hasattr(response, 'data') and 'error' in response.data:
                        print(f"   Error: {response.data['error']}")
                except:
                    pass
                error_results.append(True)
            else:
                print(f"❌ FAIL - Expected {test['expected_status']}, got {response.status_code}")
                error_results.append(False)
                
        except Exception as e:
            print(f"❌ FAIL - Exception: {str(e)}")
            error_results.append(False)
        
        print("-" * 40)
    
    error_passed = sum(error_results)
    error_total = len(error_results)
    print(f"\nError Tests: {error_passed}/{error_total} passed")
    
    return error_passed == error_total

def show_sample_response():
    """Show a sample response from the refactored API"""
    print("\n" + "=" * 80)
    print("SAMPLE RESPONSE FROM REFACTORED API")
    print("=" * 80)
    
    try:
        produto = Produtos.objects.filter(ativo=True).first()
        if not produto:
            print("No products available")
            return
        
        viewset = EstoqueViewSet()
        request = MockRequest({
            'produto_id': str(produto.id),
            'data': (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        })
        
        response = viewset.calculate_historical_stock(request)
        
        if response.status_code == 200:
            print("Sample Historical Stock Calculation Response:")
            print(json.dumps(response.data, indent=2, default=str))
        else:
            print(f"Error response: {response.data}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Testing Refactored Historical Stock Analysis API")
    print("Focus: Historical analysis, reporting, and audit capabilities")
    print()
    
    # Run main tests
    main_success = test_historical_api()
    
    # Test error handling
    error_success = test_error_handling()
    
    # Show sample response
    show_sample_response()
    
    # Final summary
    print("\n" + "=" * 80)
    print("FINAL REFACTORING RESULTS")
    print("=" * 80)
    
    if main_success and error_success:
        print("🎉 REFACTORING SUCCESSFUL!")
        print("✅ Historical stock analysis API is fully functional")
        print("✅ Error handling works correctly")
        print("✅ API focused on proper use cases:")
        print("   - Historical stock calculations")
        print("   - Movement analysis and reporting")
        print("   - Stock timeline generation")
        print("   - Stock reset analysis")
        print("   - Comprehensive product history")
        print()
        print("🎯 API is now properly focused on historical analysis")
        print("📊 Perfect for reporting, auditing, and business intelligence")
        print("✨ No longer attempts to validate/correct current stock")
    else:
        print("⚠️  Some tests failed:")
        if not main_success:
            print("❌ Main API tests failed")
        if not error_success:
            print("❌ Error handling tests failed")
        print("\nCheck the implementation for any issues.")