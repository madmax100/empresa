#!/usr/bin/env python
"""
Script para testar o endpoint de custos fixos usando ContasPagar
"""
import requests
import json
from datetime import date, timedelta

BASE_URL = "http://127.0.0.1:8000/api"

def test_custos_fixos_contas_pagar():
    """Testa o endpoint de custos fixos usando tabela ContasPagar"""
    url = f"{BASE_URL}/relatorios/custos-fixos/"
    
    # Período de teste (últimos 365 dias para ter mais chance de encontrar dados)
    data_fim = date.today()
    data_inicio = data_fim - timedelta(days=365)
    
    params = {
        'data_inicio': data_inicio.strftime('%Y-%m-%d'),
        'data_fim': data_fim.strftime('%Y-%m-%d')
    }
    
    print("🧪 TESTANDO ENDPOINT DE CUSTOS FIXOS - CONTAS A PAGAR")
    print(f"URL: {url}")
    print(f"Período: {data_inicio} até {data_fim}")
    print("="*60)
    
    try:
        response = requests.get(url, params=params, timeout=15)
        
        print(f"Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ SUCESSO!")
            
            # Parâmetros
            parametros = data.get('parametros', {})
            print(f"\n📋 PARÂMETROS:")
            print(f"  - Período: {parametros.get('data_inicio')} até {parametros.get('data_fim')}")
            print(f"  - Filtro: {parametros.get('filtro_aplicado', 'N/A')}")
            print(f"  - Fonte: {parametros.get('fonte_dados', 'N/A')}")
            
            # Estatísticas de fornecedores
            estatisticas = data.get('estatisticas_fornecedores', {})
            print(f"\n📊 ESTATÍSTICAS DE FORNECEDORES:")
            print(f"  - Fornecedores fixos cadastrados: {estatisticas.get('total_fornecedores_fixos_cadastrados', 0)}")
            print(f"  - Fornecedores com pagamentos no período: {estatisticas.get('fornecedores_com_pagamentos_no_periodo', 0)}")
            
            # Totais gerais
            totais = data.get('totais_gerais', {})
            print(f"\n💰 TOTAIS GERAIS:")
            print(f"  - Valor original das contas: R$ {totais.get('total_valor_original', 0):,.2f}")
            print(f"  - Valor total pago: R$ {totais.get('total_valor_pago', 0):,.2f}")
            print(f"  - Total de juros: R$ {totais.get('total_juros', 0):,.2f}")
            print(f"  - Total de tarifas: R$ {totais.get('total_tarifas', 0):,.2f}")
            print(f"  - Contas pagas: {data.get('total_contas_pagas', 0)}")
            
            # Resumo por tipo
            resumo_tipo = data.get('resumo_por_tipo_fornecedor', [])
            if resumo_tipo:
                print(f"\n📈 RESUMO POR TIPO DE FORNECEDOR:")
                for item in resumo_tipo:
                    tipo = item.get('fornecedor__tipo', 'N/A')
                    total_pago = item.get('total_pago', 0)
                    qtd_contas = item.get('quantidade_contas', 0)
                    valor_original = item.get('total_valor_original', 0)
                    juros = item.get('total_juros', 0)
                    tarifas = item.get('total_tarifas', 0)
                    print(f"  - {tipo}:")
                    print(f"    * Contas pagas: {qtd_contas}")
                    print(f"    * Valor original: R$ {valor_original:,.2f}")
                    print(f"    * Valor pago: R$ {total_pago:,.2f}")
                    print(f"    * Juros: R$ {juros:,.2f}")
                    print(f"    * Tarifas: R$ {tarifas:,.2f}")
            
            # Top fornecedores
            resumo_fornecedor = data.get('resumo_por_fornecedor', [])
            if resumo_fornecedor:
                print(f"\n🏢 TOP 10 FORNECEDORES:")
                for i, item in enumerate(resumo_fornecedor[:10], 1):
                    nome = item.get('fornecedor__nome', 'N/A')
                    tipo = item.get('fornecedor__tipo', 'N/A')
                    total_pago = item.get('total_pago', 0)
                    qtd_contas = item.get('quantidade_contas', 0)
                    valor_original = item.get('total_valor_original', 0)
                    print(f"  {i}. {nome} ({tipo})")
                    print(f"     Contas: {qtd_contas} | Original: R$ {valor_original:,.2f} | Pago: R$ {total_pago:,.2f}")
            
            # Últimas contas pagas
            contas = data.get('contas_pagas', [])
            if contas:
                print(f"\n💳 ÚLTIMAS 5 CONTAS PAGAS:")
                for i, conta in enumerate(contas[:5], 1):
                    data_pag = conta.get('data_pagamento', 'N/A')
                    valor_pago = conta.get('valor_pago', 0)
                    valor_original = conta.get('valor_original', 0)
                    fornecedor = conta.get('fornecedor', 'N/A')
                    tipo_fornecedor = conta.get('fornecedor_tipo', 'N/A')
                    historico = conta.get('historico', 'N/A')[:50]
                    duplicata = conta.get('numero_duplicata', 'N/A')
                    print(f"  {i}. {data_pag} - {fornecedor} ({tipo_fornecedor})")
                    print(f"     Duplicata: {duplicata} | Original: R$ {valor_original:,.2f} | Pago: R$ {valor_pago:,.2f}")
                    print(f"     Histórico: {historico}...")
            
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
    print("🔧 TESTE DO ENDPOINT - CUSTOS FIXOS COM CONTAS A PAGAR")
    print()
    
    success = test_custos_fixos_contas_pagar()
    
    print("\n" + "="*60)
    if success:
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    else:
        print("❌ TESTE FALHOU!")

if __name__ == "__main__":
    main()
