#!/usr/bin/env python
"""
Test the stock calculation API endpoints by making actual HTTP requests
"""
import os
import sys
import django
import requests
import json
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import Produtos

def test_api_endpoints():
    """Test all stock calculation API endpoints"""
    
    # Configuration
    base_url = "http://localhost:8000/api/estoque-controle"
    
    print("=" * 80)
    print("TESTING STOCK CALCULATION API ENDPOINTS")
    print("=" * 80)
    
    # Get test products
    try:
        produtos = Produtos.objects.filter(ativo=True)[:5]
        if not produtos.exists():
            print("❌ No active products found for testing")
            return False
        
        test_produto = produtos.first()
        produto_ids = [str(p.id) for p in produtos]
        
        print(f"✓ Using test product: {test_produto.codigo} - {test_produto.nome}")
        print(f"✓ Product ID: {test_produto.id}")
        print(f"✓ Test product IDs: {', '.join(produto_ids)}")
        print()
        
    except Exception as e:
        print(f"❌ Error getting test products: {str(e)}")
        return False
    
    # Test data
    today = date.today().strftime('%Y-%m-%d')
    
    # Define test cases
    test_cases = [
        {
            'name': 'Calculate Historical Stock',
            'endpoint': f'{base_url}/calculate_historical_stock/',
            'params': {
                'produto_id': test_produto.id,
                'data': today
            },
            'expected_keys': ['produto', 'calculation', 'stock_reset_info', 'movement_summary']
        },
        {
            'name': 'Validate Current Stock (Specific Products)',
            'endpoint': f'{base_url}/validate_current_stock/',
            'params': {
                'produto_ids': ','.join(produto_ids),
                'limit': 5
            },
            'expected_keys': ['validation_results', 'parameters']
        },
        {
            'name': 'Validate Current Stock (Sample)',
            'endpoint': f'{base_url}/validate_current_stock/',
            'params': {
                'limit': 10
            },
            'expected_keys': ['validation_results', 'parameters']
        },
        {
            'name': 'Stock Discrepancies',
            'endpoint': f'{base_url}/stock_discrepancies/',
            'params': {
                'threshold': '1.0',
                'limit': 10
            },
            'expected_keys': ['discrepancies', 'summary', 'parameters']
        },
        {
            'name': 'Validation Report (Specific Products)',
            'endpoint': f'{base_url}/validation_report/',
            'params': {
                'produto_ids': ','.join(produto_ids[:3])
            },
            'expected_keys': ['total_products', 'correct_stock', 'incorrect_stock', 'summary', 'analysis']
        },
        {
            'name': 'Validation Report (Sample)',
            'endpoint': f'{base_url}/validation_report/',
            'params': {
                'sample_size': 20
            },
            'expected_keys': ['total_products', 'correct_stock', 'incorrect_stock', 'summary', 'analysis']
        },
        {
            'name': 'Product Stock Detail',
            'endpoint': f'{base_url}/product_stock_detail/',
            'params': {
                'produto_id': test_produto.id,
                'days_history': 30
            },
            'expected_keys': ['product_validation', 'current_stock_comparison', 'movement_history', 'metadata']
        }
    ]
    
    # Run tests
    results = []
    for test_case in test_cases:
        print(f"Testing: {test_case['name']}")
        print(f"URL: {test_case['endpoint']}")
        print(f"Params: {test_case['params']}")
        
        try:
            # Make the request
            response = requests.get(test_case['endpoint'], params=test_case['params'], timeout=30)
            
            # Check response
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Validate expected keys
                    missing_keys = []
                    for key in test_case['expected_keys']:
                        if key not in data:
                            missing_keys.append(key)
                    
                    if missing_keys:
                        print(f"❌ FAIL - Missing keys: {missing_keys}")
                        results.append(False)
                    else:
                        print(f"✅ PASS - All expected keys present")
                        
                        # Show some key data
                        if 'produto' in data:
                            produto_info = data['produto']
                            print(f"   Product: {produto_info.get('codigo')} - {produto_info.get('nome', '')[:40]}")
                        
                        if 'calculation' in data:
                            calc = data['calculation']
                            print(f"   Calculated Stock: {calc.get('calculated_stock')}")
                            print(f"   Stored Stock: {calc.get('stored_stock')}")
                            print(f"   Is Accurate: {calc.get('is_accurate')}")
                        
                        if 'validation_results' in data:
                            val_results = data['validation_results']
                            print(f"   Total Products: {val_results.get('total_products')}")
                            print(f"   Accuracy: {val_results.get('summary', {}).get('accuracy_percentage', 0):.1f}%")
                        
                        if 'discrepancies' in data:
                            discrepancies = data['discrepancies']
                            summary = data.get('summary', {})
                            print(f"   Discrepancies Found: {len(discrepancies)}")
                            print(f"   Total in DB: {summary.get('total_discrepancies_found', 0)}")
                        
                        if 'total_products' in data:
                            print(f"   Total Products: {data.get('total_products')}")
                            print(f"   Accuracy: {data.get('summary', {}).get('accuracy_percentage', 0):.1f}%")
                        
                        if 'product_validation' in data:
                            prod_val = data['product_validation']
                            print(f"   Product: {prod_val.get('produto_codigo')} - {prod_val.get('produto_nome', '')[:40]}")
                            print(f"   Is Correct: {prod_val.get('is_correct')}")
                        
                        results.append(True)
                        
                except json.JSONDecodeError:
                    print(f"❌ FAIL - Invalid JSON response")
                    print(f"   Response: {response.text[:200]}...")
                    results.append(False)
            else:
                print(f"❌ FAIL - HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"   Response: {response.text[:200]}...")
                results.append(False)
                
        except requests.exceptions.ConnectionError:
            print(f"❌ FAIL - Connection refused (Is Django server running?)")
            print(f"   Start server with: python manage.py runserver")
            results.append(False)
        except requests.exceptions.Timeout:
            print(f"❌ FAIL - Request timeout (>30s)")
            results.append(False)
        except Exception as e:
            print(f"❌ FAIL - Unexpected error: {str(e)}")
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
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! API endpoints are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

def test_error_handling():
    """Test error handling scenarios"""
    print("\n" + "=" * 80)
    print("TESTING ERROR HANDLING")
    print("=" * 80)
    
    base_url = "http://localhost:8000/api/estoque-controle"
    
    error_test_cases = [
        {
            'name': 'Missing produto_id',
            'endpoint': f'{base_url}/calculate_historical_stock/',
            'params': {'data': '2025-09-14'},
            'expected_status': 400
        },
        {
            'name': 'Invalid produto_id',
            'endpoint': f'{base_url}/calculate_historical_stock/',
            'params': {'produto_id': 'invalid', 'data': '2025-09-14'},
            'expected_status': 400
        },
        {
            'name': 'Invalid date format',
            'endpoint': f'{base_url}/calculate_historical_stock/',
            'params': {'produto_id': 1, 'data': 'invalid-date'},
            'expected_status': 400
        },
        {
            'name': 'Non-existent produto_id',
            'endpoint': f'{base_url}/calculate_historical_stock/',
            'params': {'produto_id': 999999, 'data': '2025-09-14'},
            'expected_status': 404
        }
    ]
    
    error_results = []
    for test_case in error_test_cases:
        print(f"Testing: {test_case['name']}")
        
        try:
            response = requests.get(test_case['endpoint'], params=test_case['params'], timeout=10)
            
            if response.status_code == test_case['expected_status']:
                print(f"✅ PASS - Got expected status {response.status_code}")
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        print(f"   Error message: {error_data['error']}")
                    error_results.append(True)
                except:
                    print(f"   Response: {response.text}")
                    error_results.append(True)
            else:
                print(f"❌ FAIL - Expected {test_case['expected_status']}, got {response.status_code}")
                error_results.append(False)
                
        except requests.exceptions.ConnectionError:
            print(f"❌ FAIL - Connection refused")
            error_results.append(False)
        except Exception as e:
            print(f"❌ FAIL - Error: {str(e)}")
            error_results.append(False)
        
        print("-" * 40)
    
    error_passed = sum(error_results)
    error_total = len(error_results)
    
    print(f"\nError Handling Tests: {error_passed}/{error_total} passed")
    return error_passed == error_total

def show_usage_examples():
    """Show practical usage examples"""
    print("\n" + "=" * 80)
    print("USAGE EXAMPLES")
    print("=" * 80)
    
    base_url = "http://localhost:8000/api/estoque-controle"
    
    try:
        produto = Produtos.objects.filter(ativo=True).first()
        produto_id = produto.id if produto else 1
    except:
        produto_id = 1
    
    today = date.today().strftime('%Y-%m-%d')
    
    examples = [
        {
            'description': 'Check if a product has accurate stock',
            'command': f'curl "{base_url}/calculate_historical_stock/?produto_id={produto_id}&data={today}"'
        },
        {
            'description': 'Find top 20 products with stock discrepancies',
            'command': f'curl "{base_url}/stock_discrepancies/?threshold=1.0&limit=20"'
        },
        {
            'description': 'Validate stock accuracy for 100 products',
            'command': f'curl "{base_url}/validate_current_stock/?limit=100"'
        },
        {
            'description': 'Get comprehensive validation report',
            'command': f'curl "{base_url}/validation_report/?sample_size=200"'
        },
        {
            'description': 'Analyze specific product in detail',
            'command': f'curl "{base_url}/product_stock_detail/?produto_id={produto_id}&days_history=60"'
        }
    ]
    
    for example in examples:
        print(f"\n{example['description']}:")
        print(f"{example['command']}")
    
    print(f"\nNote: Replace localhost:8000 with your actual server URL")

if __name__ == "__main__":
    print("🚀 Starting API endpoint tests...")
    print("Make sure Django server is running: python manage.py runserver")
    print()
    
    # Run main tests
    main_success = test_api_endpoints()
    
    # Run error handling tests
    error_success = test_error_handling()
    
    # Show usage examples
    show_usage_examples()
    
    # Final result
    print("\n" + "=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    
    if main_success and error_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ API endpoints are working correctly")
        print("✅ Error handling is working correctly")
        print("✅ The stock calculation API is ready for production use")
    else:
        print("⚠️  Some tests failed:")
        if not main_success:
            print("❌ Main API functionality tests failed")
        if not error_success:
            print("❌ Error handling tests failed")
        print("\nCheck the Django server logs for more details.")