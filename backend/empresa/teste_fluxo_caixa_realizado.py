#!/usr/bin/env python
"""
Script para verificar todos os endpoints do fluxo-caixa-realizado
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/fluxo-caixa-realizado"

def test_endpoint(url, name):
    """Testa um endpoint específico"""
    print(f"{'='*50}")
    print(f"Testando: {name}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCESSO!")
            try:
                data = response.json()
                if isinstance(data, dict):
                    print("Chaves principais:")
                    for key in list(data.keys())[:5]:  # Mostra apenas as primeiras 5 chaves
                        print(f"  - {key}")
                        
            except json.JSONDecodeError:
                print("❌ Resposta não é JSON válido")
        else:
            print(f"❌ ERRO - Status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Erro: {error_data}")
            except:
                print(f"Erro texto: {response.text[:200]}...")
                
    except Exception as e:
        print(f"❌ EXCEÇÃO: {str(e)}")

def main():
    """Testa todos os endpoints do fluxo-caixa-realizado"""
    print("🔍 TESTANDO ENDPOINTS FLUXO-CAIXA-REALIZADO")
    
    # Parâmetros de data para os testes
    data_params = "?data_inicio=2025-08-01&data_fim=2025-09-06"
    
    endpoints = [
        (f"/movimentacoes_realizadas/{data_params}", "Movimentações Realizadas"),
        (f"/resumo_mensal/{data_params}", "Resumo Mensal"),
        (f"/resumo_diario/{data_params}", "Resumo Diário"),
        (f"/movimentacoes_vencimento_aberto/{data_params}", "Movimentações Vencimento Aberto"),
    ]
    
    success_count = 0
    total_count = len(endpoints)
    
    for endpoint_url, name in endpoints:
        test_endpoint(f"{BASE_URL}{endpoint_url}", name)
        # Verifica se foi sucesso para contar
        try:
            resp = requests.get(f"{BASE_URL}{endpoint_url}", timeout=5)
            if resp.status_code == 200:
                success_count += 1
        except:
            pass
        print()
    
    print("="*60)
    print(f"📊 RESULTADO FINAL: {success_count}/{total_count} endpoints funcionando")
    print(f"Taxa de sucesso: {(success_count/total_count)*100:.1f}%")
    
    if success_count == total_count:
        print("🎉 TODOS OS ENDPOINTS ESTÃO FUNCIONANDO!")
    else:
        print(f"⚠️  {total_count - success_count} endpoint(s) precisam de correção")

if __name__ == "__main__":
    main()
