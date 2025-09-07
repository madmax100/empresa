#!/usr/bin/env python3
"""
Teste do novo endpoint de contas por data de pagamento
"""

import requests
import json
from datetime import datetime, timedelta

# Configuração da API
BASE_URL = 'http://localhost:8000'
ENDPOINT = '/contas/contas-por-data-pagamento/'

def testar_endpoint():
    """Testa o endpoint de contas por data de pagamento"""
    
    print("🧪 TESTE DO ENDPOINT: Contas por Data de Pagamento")
    print("=" * 60)
    
    # Definir datas de teste (últimos 30 dias)
    data_fim = datetime.now().date()
    data_inicio = data_fim - timedelta(days=30)
    
    # Teste 1: Buscar todas as contas pagas nos últimos 30 dias
    print("\n📊 TESTE 1: Todas as contas pagas (últimos 30 dias)")
    print(f"Período: {data_inicio} a {data_fim}")
    
    params = {
        'data_inicio': data_inicio.strftime('%Y-%m-%d'),
        'data_fim': data_fim.strftime('%Y-%m-%d'),
        'tipo': 'ambos',
        'status': 'P'
    }
    
    try:
        response = requests.get(f"{BASE_URL}{ENDPOINT}", params=params)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso!")
            print(f"📋 Resumo:")
            print(f"  - Contas a Pagar: {data['resumo']['total_contas_pagar']}")
            print(f"  - Valor Pago (Fornecedores): R$ {data['resumo']['valor_total_pagar']}")
            print(f"  - Contas a Receber: {data['resumo']['total_contas_receber']}")
            print(f"  - Valor Recebido (Clientes): R$ {data['resumo']['valor_total_receber']}")
            
            if 'saldo_liquido' in data['resumo']:
                print(f"  - Saldo Líquido: R$ {data['resumo']['saldo_liquido']}")
            
            # Mostrar alguns exemplos se houver dados
            if data['contas_a_pagar']:
                print(f"\n💰 Primeiras 3 Contas a Pagar:")
                for i, conta in enumerate(data['contas_a_pagar'][:3]):
                    print(f"  {i+1}. {conta.get('fornecedor_nome', 'N/A')} - R$ {conta.get('valor_pago', 0)} - {conta.get('data_pagamento', 'N/A')}")
            
            if data['contas_a_receber']:
                print(f"\n💸 Primeiras 3 Contas a Receber:")
                for i, conta in enumerate(data['contas_a_receber'][:3]):
                    print(f"  {i+1}. {conta.get('cliente_nome', 'N/A')} - R$ {conta.get('recebido', 0)} - {conta.get('data_pagamento', 'N/A')}")
                    
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 2: Apenas contas a pagar
    print("\n" + "=" * 60)
    print("📊 TESTE 2: Apenas Contas a Pagar")
    
    params_pagar = {
        'data_inicio': data_inicio.strftime('%Y-%m-%d'),
        'data_fim': data_fim.strftime('%Y-%m-%d'),
        'tipo': 'pagar',
        'status': 'P'
    }
    
    try:
        response = requests.get(f"{BASE_URL}{ENDPOINT}", params=params_pagar)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso!")
            print(f"📋 Resumo Contas a Pagar:")
            print(f"  - Total de Contas: {data['resumo']['total_contas_pagar']}")
            print(f"  - Valor Total Pago: R$ {data['resumo']['valor_total_pagar']}")
            print(f"  - Contas a Receber: {data['resumo']['total_contas_receber']} (deve ser 0)")
            
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 3: Apenas contas a receber
    print("\n" + "=" * 60)
    print("📊 TESTE 3: Apenas Contas a Receber")
    
    params_receber = {
        'data_inicio': data_inicio.strftime('%Y-%m-%d'),
        'data_fim': data_fim.strftime('%Y-%m-%d'),
        'tipo': 'receber',
        'status': 'P'
    }
    
    try:
        response = requests.get(f"{BASE_URL}{ENDPOINT}", params=params_receber)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso!")
            print(f"📋 Resumo Contas a Receber:")
            print(f"  - Contas a Pagar: {data['resumo']['total_contas_pagar']} (deve ser 0)")
            print(f"  - Total de Contas: {data['resumo']['total_contas_receber']}")
            print(f"  - Valor Total Recebido: R$ {data['resumo']['valor_total_receber']}")
            
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 4: Teste de validação (sem parâmetros)
    print("\n" + "=" * 60)
    print("📊 TESTE 4: Validação (sem parâmetros obrigatórios)")
    
    try:
        response = requests.get(f"{BASE_URL}{ENDPOINT}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 400:
            data = response.json()
            print(f"✅ Validação funcionando!")
            print(f"Erro esperado: {data.get('error')}")
        else:
            print(f"❌ Esperado status 400, recebido: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 TESTES CONCLUÍDOS!")
    print("\n📝 INSTRUÇÕES PARA USO:")
    print(f"URL: {BASE_URL}{ENDPOINT}")
    print("Parâmetros obrigatórios:")
    print("  - data_inicio: YYYY-MM-DD")
    print("  - data_fim: YYYY-MM-DD")
    print("Parâmetros opcionais:")
    print("  - tipo: 'pagar', 'receber' ou 'ambos' (padrão: 'ambos')")
    print("  - status: 'P', 'A', 'C' ou 'TODOS' (padrão: 'P')")

if __name__ == "__main__":
    testar_endpoint()
