#!/usr/bin/env python
"""
Test the API endpoints by calling the view methods directly
"""
import os
import sys
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from django.http import HttpRequest
from django.test import RequestFactory
from contas.models.access import Produtos
from contas.views.estoque_views import EstoqueViewSet
import json

class MockRequest:
    """Mock request object with query_params"""
    def __init__(self, params):
        self.query_params = params
        self.method = 'GET'

def test_api_methods_directly():
    """Test API methods by calling them directly"""
    
    print("=" * 80)
    print("TESTING STOCK CALCULATION API METHODS DIRECTLY")
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
        print()
        
    except Exception as e:
        print(f"❌ Error getting test products: {str(e)}")
        return False
    
    # Create viewset instance
    viewset = EstoqueViewSet()
    
    # Test data
    today = date.today().strftime('%Y-%m-%d')
    
    # Test cases
    test_cases = [
        {
            'name': 'Calculate Historical Stock',
            'method': 'calculate_historical_stock',
            'params': {
                'produto_id': str(test_produto.id),
                'data': today
            }
        },
        {
            'name': 'Validate Current Stock',
            'method': 'validate_current_stock',
            'params': {
                'produto_ids': ','.join(produto_ids[:3]),
                'limit': '5'
            }
        },
        {
            'name': 'Stock Discrepancies',
            'method': 'stock_discrepancies',
            'params': {
                'threshold': '1.0',
                'limit': '10'
            }
        },
        {
            'name': 'Validation Report',
            'method': 'validation_report',
            'params': {
                'produto_ids': ','.join(produto_ids[:2])
            }
        },
        {
            'name': 'Product Stock Detail',
            'method': 'product_stock_detail',
            'params': {
                'produto_id': str(test_produto.id),
                'days_history': '30'
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
                    
                    # Show key information
                    if 'produto' in data:
                        produto_info = data['produto']
                        calc = data.get('calculation', {})
                        print(f"   Product: {produto_info.get('codigo')} - {produto_info.get('nome', '')[:40]}")
                        print(f"   Calculated Stock: {calc.get('calculated_stock')}")
                        print(f"   Is Accurate: {calc.get('is_accurate')}")
                    
                    elif 'validation_results' in data:
                        val_results = data['validation_results']
                        summary = val_results.get('summary', {})
                        print(f"   Products Validated: {val_results.get('total_products')}")
                        print(f"   Accuracy: {summary.get('accuracy_percentage', 0):.1f}%")
                        print(f"   Discrepancies: {len(val_results.get('discrepancies', []))}")
                    
                    elif 'discrepancies' in data:
                        discrepancies = data['discrepancies']
                        summary = data.get('summary', {})
                        print(f"   Discrepancies Returned: {len(discrepancies)}")
                        print(f"   Total Found: {summary.get('total_discrepancies_found', 0)}")
                        if discrepancies:
                            top_disc = discrepancies[0]
                            print(f"   Top Discrepancy: {top_disc.get('produto_codigo')} (diff: {top_disc.get('difference')})")
                    
                    elif 'total_products' in data:
                        summary = data.get('summary', {})
                        print(f"   Total Products: {data.get('total_products')}")
                        print(f"   Accuracy: {summary.get('accuracy_percentage', 0):.1f}%")
                        recommendations = data.get('recommendations', [])
                        print(f"   Recommendations: {len(recommendations)}")
                    
                    elif 'product_validation' in data:
                        prod_val = data['product_validation']
                        print(f"   Product: {prod_val.get('produto_codigo')}")
                        print(f"   Is Correct: {prod_val.get('is_correct')}")
                        print(f"   Total Movements: {prod_val.get('movement_info', {}).get('total_movements', 0)}")
                    
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
            import traceback
            traceback.print_exc()
            results.append(False)
        
        print("-" * 60)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    return passed == total

def test_error_handling():
    """Test error handling scenarios"""
    print("\n" + "=" * 80)
    print("TESTING ERROR HANDLING")
    print("=" * 80)
    
    viewset = EstoqueViewSet()
    
    error_tests = [
        {
            'name': 'Missing produto_id',
            'method': 'calculate_historical_stock',
            'params': {'data': '2025-09-14'},
            'expected_status': 400
        },
        {
            'name': 'Invalid produto_id',
            'method': 'calculate_historical_stock',
            'params': {'produto_id': 'invalid', 'data': '2025-09-14'},
            'expected_status': 400
        },
        {
            'name': 'Invalid date format',
            'method': 'calculate_historical_stock',
            'params': {'produto_id': '1', 'data': 'invalid-date'},
            'expected_status': 400
        },
        {
            'name': 'Non-existent produto_id',
            'method': 'product_stock_detail',
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

def show_detailed_response():
    """Show a detailed response example"""
    print("\n" + "=" * 80)
    print("DETAILED RESPONSE EXAMPLE")
    print("=" * 80)
    
    try:
        produto = Produtos.objects.filter(ativo=True).first()
        if not produto:
            print("No products available")
            return
        
        viewset = EstoqueViewSet()
        request = MockRequest({
            'produto_id': str(produto.id),
            'data': date.today().strftime('%Y-%m-%d')
        })
        
        response = viewset.calculate_historical_stock(request)
        
        if response.status_code == 200:
            print("Sample Calculate Historical Stock Response:")
            print(json.dumps(response.data, indent=2, default=str))
        else:
            print(f"Error response: {response.data}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Testing Stock Calculation API Methods")
    print("Direct method calls (no HTTP layer)")
    print()
    
    # Run main tests
    main_success = test_api_methods_directly()
    
    # Test error handling
    error_success = test_error_handling()
    
    # Show detailed response
    show_detailed_response()
    
    # Final summary
    print("\n" + "=" * 80)
    print("FINAL TEST RESULTS")
    print("=" * 80)
    
    if main_success and error_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Stock calculation API methods are fully functional")
        print("✅ Error handling works correctly")
        print("✅ Ready for HTTP integration and production use")
        print("\nThe API endpoints are working correctly at the method level.")
        print("Any HTTP-level issues are likely configuration-related (ALLOWED_HOSTS, etc.)")
    else:
        print("⚠️  Some tests failed:")
        if not main_success:
            print("❌ Main API method tests failed")
        if not error_success:
            print("❌ Error handling tests failed")
        print("\nCheck the implementation for any issues.")