#!/usr/bin/env python
"""
Script para testar o endpoint de custos fixos corrigido
"""
import requests
import json
from datetime import date, timedelta

BASE_URL = "http://127.0.0.1:8000/api"

def test_custos_fixos_endpoint():
    """Testa o endpoint de custos fixos por fornecedores"""
    url = f"{BASE_URL}/relatorios/custos-fixos/"
    
    # Período de teste (últimos 30 dias)
    data_fim = date.today()
    data_inicio = data_fim - timedelta(days=30)
    
    params = {
        'data_inicio': data_inicio.strftime('%Y-%m-%d'),
        'data_fim': data_fim.strftime('%Y-%m-%d')
    }
    
    print("🧪 TESTANDO ENDPOINT DE CUSTOS FIXOS")
    print(f"URL: {url}")
    print(f"Período: {data_inicio} até {data_fim}")
    print("="*50)
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        print(f"Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ SUCESSO!")
            print(f"Parâmetros utilizados: {data.get('parametros', {})}")
            
            estatisticas = data.get('estatisticas_fornecedores', {})
            print(f"\n📊 ESTATÍSTICAS DE FORNECEDORES:")
            print(f"  - Fornecedores fixos cadastrados: {estatisticas.get('total_fornecedores_fixos_cadastrados', 0)}")
            print(f"  - Fornecedores com pagamentos no período: {estatisticas.get('fornecedores_com_pagamentos_no_periodo', 0)}")
            
            print(f"\n💰 RESUMO FINANCEIRO:")
            print(f"  - Total geral pago: R$ {data.get('total_geral_pago', 0):,.2f}")
            print(f"  - Total de lançamentos: {data.get('total_lancamentos', 0)}")
            
            resumo_tipo = data.get('resumo_por_tipo_fornecedor', [])
            if resumo_tipo:
                print(f"\n📋 RESUMO POR TIPO DE FORNECEDOR:")
                for item in resumo_tipo:
                    tipo = item.get('fornecedor__tipo', 'N/A')
                    total = item.get('total_pago', 0)
                    qtd = item.get('quantidade_lancamentos', 0)
                    print(f"  - {tipo}: R$ {total:,.2f} ({qtd} lançamentos)")
            
            resumo_fornecedor = data.get('resumo_por_fornecedor', [])
            if resumo_fornecedor:
                print(f"\n🏢 TOP 10 FORNECEDORES:")
                for i, item in enumerate(resumo_fornecedor[:10], 1):
                    nome = item.get('fornecedor__nome', 'N/A')
                    tipo = item.get('fornecedor__tipo', 'N/A')
                    total = item.get('total_pago', 0)
                    qtd = item.get('quantidade_lancamentos', 0)
                    print(f"  {i}. {nome} ({tipo}): R$ {total:,.2f} ({qtd} lançamentos)")
            
            pagamentos = data.get('pagamentos', [])
            if pagamentos:
                print(f"\n💳 ÚLTIMOS 5 PAGAMENTOS:")
                for i, pagamento in enumerate(pagamentos[:5], 1):
                    data_pag = pagamento.get('data_pagamento', 'N/A')
                    valor = pagamento.get('valor', 0)
                    fornecedor = pagamento.get('fornecedor', 'N/A')
                    tipo_fornecedor = pagamento.get('fornecedor_tipo', 'N/A')
                    descricao = pagamento.get('descricao', 'N/A')[:50]
                    print(f"  {i}. {data_pag} - R$ {valor:,.2f} - {fornecedor} ({tipo_fornecedor})")
                    print(f"     {descricao}...")
            
            return True
            
        else:
            print(f"❌ ERRO - Status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Detalhes do erro: {error_data}")
            except:
                print(f"Resposta: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        return False

def main():
    """Função principal"""
    print("🔧 TESTE DO ENDPOINT CORRIGIDO - CUSTOS FIXOS POR TIPO DE FORNECEDOR")
    print()
    
    success = test_custos_fixos_endpoint()
    
    print("\n" + "="*50)
    if success:
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    else:
        print("❌ TESTE FALHOU!")

if __name__ == "__main__":
    main()
