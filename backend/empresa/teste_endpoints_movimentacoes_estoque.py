#!/usr/bin/env python3
"""
TESTE COMPLETO DOS ENDPOINTS DE MOVIMENTAÇÕES DE ESTOQUE
Status: 06/09/2025 - 04:00
"""

import requests
import json
from datetime import datetime

def test_movimentacoes_endpoints():
    """Testa todos os endpoints de movimentações de estoque"""
    
    base_url = "http://localhost:8000/api/movimentacoes_estoque"
    
    print("🧪 TESTANDO ENDPOINTS DE MOVIMENTAÇÕES DE ESTOQUE")
    print("=" * 60)
    
    tests = [
        {
            'name': 'Listagem Geral',
            'url': f"{base_url}/",
            'method': 'GET'
        },
        {
            'name': 'Detalhe de Movimentação',
            'url': f"{base_url}/219921/",
            'method': 'GET'
        },
        {
            'name': 'Filtro por Produto',
            'url': f"{base_url}/?produto=4113",
            'method': 'GET'
        },
        {
            'name': 'Filtro por Data',
            'url': f"{base_url}/?data_movimentacao=2025-01-01",
            'method': 'GET'
        },
        {
            'name': 'Paginação',
            'url': f"{base_url}/?page=1&page_size=10",
            'method': 'GET'
        }
    ]
    
    results = []
    
    for test in tests:
        try:
            print(f"\n📋 Testando: {test['name']}")
            print(f"   URL: {test['url']}")
            
            response = requests.get(test['url'])
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    count = len(data)
                    print(f"   ✅ Status: 200 OK - {count} registros")
                elif isinstance(data, dict):
                    if 'results' in data:
                        count = len(data['results'])
                        total = data.get('count', 'N/A')
                        print(f"   ✅ Status: 200 OK - {count} registros (total: {total})")
                    else:
                        print(f"   ✅ Status: 200 OK - Detalhe único")
                        if 'id' in data:
                            print(f"      ID: {data['id']}")
                            print(f"      Produto: {data.get('produto', 'N/A')}")
                            print(f"      Quantidade: {data.get('quantidade', 'N/A')}")
                            print(f"      Valor Total: R$ {data.get('valor_total', 'N/A')}")
                
                results.append({
                    'test': test['name'],
                    'status': 'SUCESSO',
                    'code': response.status_code,
                    'data_type': type(data).__name__
                })
                
            else:
                print(f"   ❌ Status: {response.status_code}")
                print(f"      Erro: {response.text[:200]}")
                results.append({
                    'test': test['name'],
                    'status': 'ERRO',
                    'code': response.status_code,
                    'error': response.text[:200]
                })
                
        except Exception as e:
            print(f"   💥 Erro: {str(e)}")
            results.append({
                'test': test['name'],
                'status': 'EXCEÇÃO',
                'error': str(e)
            })
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    sucessos = len([r for r in results if r['status'] == 'SUCESSO'])
    total = len(results)
    
    print(f"Total de testes: {total}")
    print(f"Sucessos: {sucessos}")
    print(f"Falhas: {total - sucessos}")
    print(f"Taxa de sucesso: {(sucessos/total)*100:.1f}%")
    
    if sucessos == total:
        print("\n🎉 TODOS OS ENDPOINTS ESTÃO FUNCIONANDO PERFEITAMENTE!")
    else:
        print(f"\n⚠️  {total - sucessos} endpoints precisam de correção")
    
    print("\n📋 Detalhes por endpoint:")
    for result in results:
        status_icon = "✅" if result['status'] == 'SUCESSO' else "❌"
        print(f"   {status_icon} {result['test']}: {result['status']}")

if __name__ == "__main__":
    test_movimentacoes_endpoints()
