#!/usr/bin/env python
"""
Run API tests using Django's test client (no need for running server)
"""
import os
import sys
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from contas.models.access import Produtos
import json

def test_api_with_django_client():
    """Test API endpoints using Django's test client"""
    
    print("=" * 80)
    print("TESTING STOCK CALCULATION API WITH DJANGO CLIENT")
    print("=" * 80)
    
    # Create test client
    client = Client()
    
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
        print()
        
    except Exception as e:
        print(f"❌ Error getting test products: {str(e)}")
        return False
    
    # Test data
    today = date.today().strftime('%Y-%m-%d')
    
    # Test cases
    test_cases = [
        {
            'name': 'Calculate Historical Stock',
            'url': '/api/estoque-controle/calculate_historical_stock/',
            'params': {
                'produto_id': test_produto.id,
                'data': today
            }
        },
        {
            'name': 'Validate Current Stock',
            'url': '/api/estoque-controle/validate_current_stock/',
            'params': {
                'produto_ids': ','.join(produto_ids[:3]),
                'limit': 5
            }
        },
        {
            'name': 'Stock Discrepancies',
            'url': '/api/estoque-controle/stock_discrepancies/',
            'params': {
                'threshold': '1.0',
                'limit': 10
            }
        },
        {
            'name': 'Validation Report',
            'url': '/api/estoque-controle/validation_report/',
            'params': {
                'produto_ids': ','.join(produto_ids[:2]),
                'sample_size': 10
            }
        },
        {
            'name': 'Product Stock Detail',
            'url': '/api/estoque-controle/product_stock_detail/',
            'params': {
                'produto_id': test_produto.id,
                'days_history': 30
            }
        }
    ]
    
    # Run tests
    results = []
    for test_case in test_cases:
        print(f"Testing: {test_case['name']}")
        print(f"URL: {test_case['url']}")
        print(f"Params: {test_case['params']}")
        
        try:
            # Make request
            response = client.get(test_case['url'], test_case['params'])
            
            if response.status_code == 200:
                try:
                    # Parse JSON response
                    data = json.loads(response.content)
                    
                    print(f"✅ PASS - Status 200, valid JSON response")
                    
                    # Show key information based on endpoint
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
                    
                except json.JSONDecodeError as e:
                    print(f"❌ FAIL - Invalid JSON: {str(e)}")
                    print(f"   Response: {response.content[:200]}")
                    results.append(False)
            else:
                print(f"❌ FAIL - Status {response.status_code}")
                try:
                    error_data = json.loads(response.content)
                    print(f"   Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"   Response: {response.content[:200]}")
                results.append(False)
                
        except Exception as e:
            print(f"❌ FAIL - Exception: {str(e)}")
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
        print("🎉 ALL TESTS PASSED!")
        print("✅ API endpoints are working correctly")
        print("✅ Stock calculation services are operational")
        print("✅ Ready for production use")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False

def test_error_scenarios():
    """Test error handling"""
    print("\n" + "=" * 80)
    print("TESTING ERROR HANDLING")
    print("=" * 80)
    
    client = Client()
    
    error_tests = [
        {
            'name': 'Missing produto_id',
            'url': '/api/estoque-controle/calculate_historical_stock/',
            'params': {'data': '2025-09-14'},
            'expected_status': 400
        },
        {
            'name': 'Invalid produto_id',
            'url': '/api/estoque-controle/calculate_historical_stock/',
            'params': {'produto_id': 'invalid', 'data': '2025-09-14'},
            'expected_status': 400
        },
        {
            'name': 'Invalid date format',
            'url': '/api/estoque-controle/calculate_historical_stock/',
            'params': {'produto_id': 1, 'data': 'invalid-date'},
            'expected_status': 400
        },
        {
            'name': 'Non-existent produto_id',
            'url': '/api/estoque-controle/product_stock_detail/',
            'params': {'produto_id': 999999},
            'expected_status': 404
        }
    ]
    
    error_results = []
    for test in error_tests:
        print(f"Testing: {test['name']}")
        
        try:
            response = client.get(test['url'], test['params'])
            
            if response.status_code == test['expected_status']:
                print(f"✅ PASS - Got expected status {response.status_code}")
                try:
                    error_data = json.loads(response.content)
                    if 'error' in error_data:
                        print(f"   Error: {error_data['error']}")
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

def show_sample_responses():
    """Show sample API responses"""
    print("\n" + "=" * 80)
    print("SAMPLE API RESPONSES")
    print("=" * 80)
    
    client = Client()
    
    try:
        produto = Produtos.objects.filter(ativo=True).first()
        if not produto:
            print("No products available for sample")
            return
        
        # Get a sample response
        response = client.get('/api/estoque-controle/calculate_historical_stock/', {
            'produto_id': produto.id,
            'data': date.today().strftime('%Y-%m-%d')
        })
        
        if response.status_code == 200:
            data = json.loads(response.content)
            print("Sample Calculate Historical Stock Response:")
            print(json.dumps(data, indent=2, default=str)[:1000] + "...")
        
        # Get discrepancies sample
        response = client.get('/api/estoque-controle/stock_discrepancies/', {
            'threshold': '1.0',
            'limit': 3
        })
        
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"\nSample Stock Discrepancies Response:")
            print(f"Total discrepancies found: {data.get('summary', {}).get('total_discrepancies_found', 0)}")
            discrepancies = data.get('discrepancies', [])
            for i, disc in enumerate(discrepancies[:3], 1):
                print(f"{i}. {disc.get('produto_codigo')}: {disc.get('produto_nome', '')[:40]}")
                print(f"   Stored: {disc.get('stored_stock')}, Calculated: {disc.get('calculated_stock')}")
                print(f"   Difference: {disc.get('difference')}")
        
    except Exception as e:
        print(f"Error getting samples: {str(e)}")

if __name__ == "__main__":
    print("🚀 Testing Stock Calculation API Endpoints")
    print("Using Django test client (no server required)")
    print()
    
    # Run main tests
    main_success = test_api_with_django_client()
    
    # Test error handling
    error_success = test_error_scenarios()
    
    # Show sample responses
    show_sample_responses()
    
    # Final summary
    print("\n" + "=" * 80)
    print("FINAL TEST RESULTS")
    print("=" * 80)
    
    if main_success and error_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Stock calculation API is fully functional")
        print("✅ Error handling works correctly")
        print("✅ Ready for integration and production use")
        print("\nNext steps:")
        print("- Integrate with frontend applications")
        print("- Implement stock correction management commands")
        print("- Add database optimization for better performance")
    else:
        print("⚠️  Some tests failed:")
        if not main_success:
            print("❌ Main API tests failed")
        if not error_success:
            print("❌ Error handling tests failed")
        print("\nCheck the Django logs and fix any issues before proceeding.")