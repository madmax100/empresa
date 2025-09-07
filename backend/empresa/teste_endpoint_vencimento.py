#!/usr/bin/env python3
"""
Teste do novo endpoint de contas por data de vencimento
"""

import requests
import json
from datetime import datetime, timedelta

# Configuração da API
BASE_URL = 'http://localhost:8000'
ENDPOINT = '/contas/contas-por-data-vencimento/'

def testar_endpoint():
    """Testa o endpoint de contas por data de vencimento"""
    
    print("🧪 TESTE DO ENDPOINT: Contas por Data de Vencimento")
    print("=" * 60)
    
    # Definir datas de teste (próximos 30 dias)
    data_inicio = datetime.now().date()
    data_fim = data_inicio + timedelta(days=30)
    
    # Teste 1: Buscar todas as contas com vencimento nos próximos 30 dias
    print("\n📊 TESTE 1: Todas as contas em aberto (próximos 30 dias)")
    print(f"Período: {data_inicio} a {data_fim}")
    
    params = {
        'data_inicio': data_inicio.strftime('%Y-%m-%d'),
        'data_fim': data_fim.strftime('%Y-%m-%d'),
        'tipo': 'ambos',
        'status': 'A'
    }
    
    try:
        response = requests.get(f"{BASE_URL}{ENDPOINT}", params=params)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso!")
            print(f"📋 Resumo:")
            print(f"  - Contas a Pagar: {data['resumo']['total_contas_pagar']}")
            print(f"  - Valor a Pagar: R$ {data['resumo']['valor_total_pagar']}")
            print(f"  - Contas Vencidas (Pagar): {data['resumo']['contas_vencidas_pagar']}")
            print(f"  - Valor Vencido (Pagar): R$ {data['resumo']['valor_vencidas_pagar']}")
            print(f"  - Contas a Receber: {data['resumo']['total_contas_receber']}")
            print(f"  - Valor a Receber: R$ {data['resumo']['valor_total_receber']}")
            print(f"  - Contas Vencidas (Receber): {data['resumo']['contas_vencidas_receber']}")
            print(f"  - Valor Vencido (Receber): R$ {data['resumo']['valor_vencidas_receber']}")
            
            if 'saldo_previsto' in data['resumo']:
                print(f"  - Saldo Previsto: R$ {data['resumo']['saldo_previsto']}")
            if 'saldo_vencidas' in data['resumo']:
                print(f"  - Saldo Vencidas: R$ {data['resumo']['saldo_vencidas']}")
            
            # Mostrar alguns exemplos se houver dados
            if data['contas_a_pagar']:
                print(f"\n💰 Primeiras 3 Contas a Pagar:")
                for i, conta in enumerate(data['contas_a_pagar'][:3]):
                    vencimento = conta.get('vencimento', 'N/A')
                    if vencimento != 'N/A':
                        vencimento = datetime.fromisoformat(vencimento.replace('Z', '')).strftime('%d/%m/%Y')
                    print(f"  {i+1}. {conta.get('fornecedor_nome', 'N/A')} - R$ {conta.get('valor', 0)} - Venc: {vencimento}")
            
            if data['contas_a_receber']:
                print(f"\n💸 Primeiras 3 Contas a Receber:")
                for i, conta in enumerate(data['contas_a_receber'][:3]):
                    vencimento = conta.get('vencimento', 'N/A')
                    if vencimento != 'N/A':
                        vencimento = datetime.fromisoformat(vencimento.replace('Z', '')).strftime('%d/%m/%Y')
                    print(f"  {i+1}. {conta.get('cliente_nome', 'N/A')} - R$ {conta.get('valor', 0)} - Venc: {vencimento}")
                    
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 2: Apenas contas a pagar vencendo
    print("\n" + "=" * 60)
    print("📊 TESTE 2: Apenas Contas a Pagar (próximos 7 dias)")
    
    data_fim_7dias = data_inicio + timedelta(days=7)
    params_pagar = {
        'data_inicio': data_inicio.strftime('%Y-%m-%d'),
        'data_fim': data_fim_7dias.strftime('%Y-%m-%d'),
        'tipo': 'pagar',
        'status': 'A'
    }
    
    try:
        response = requests.get(f"{BASE_URL}{ENDPOINT}", params=params_pagar)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso!")
            print(f"📋 Resumo Contas a Pagar (7 dias):")
            print(f"  - Total de Contas: {data['resumo']['total_contas_pagar']}")
            print(f"  - Valor Total: R$ {data['resumo']['valor_total_pagar']}")
            print(f"  - Contas Vencidas: {data['resumo']['contas_vencidas_pagar']}")
            print(f"  - Valor Vencido: R$ {data['resumo']['valor_vencidas_pagar']}")
            print(f"  - Contas a Receber: {data['resumo']['total_contas_receber']} (deve ser 0)")
            
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 3: Contas já vencidas (últimos 30 dias)
    print("\n" + "=" * 60)
    print("📊 TESTE 3: Contas Vencidas (últimos 30 dias)")
    
    data_inicio_vencidas = data_inicio - timedelta(days=30)
    data_fim_vencidas = data_inicio - timedelta(days=1)
    
    params_vencidas = {
        'data_inicio': data_inicio_vencidas.strftime('%Y-%m-%d'),
        'data_fim': data_fim_vencidas.strftime('%Y-%m-%d'),
        'tipo': 'ambos',
        'status': 'A'
    }
    
    try:
        response = requests.get(f"{BASE_URL}{ENDPOINT}", params=params_vencidas)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso!")
            print(f"📋 Resumo Contas Vencidas:")
            print(f"  - Contas a Pagar Vencidas: {data['resumo']['total_contas_pagar']}")
            print(f"  - Valor a Pagar Vencido: R$ {data['resumo']['valor_total_pagar']}")
            print(f"  - Contas a Receber Vencidas: {data['resumo']['total_contas_receber']}")
            print(f"  - Valor a Receber Vencido: R$ {data['resumo']['valor_total_receber']}")
            
            if 'saldo_previsto' in data['resumo']:
                print(f"  - Saldo das Vencidas: R$ {data['resumo']['saldo_previsto']}")
            
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 4: Todas as contas (pagas e não pagas)
    print("\n" + "=" * 60)
    print("📊 TESTE 4: Todas as Contas (pagas e não pagas - próximos 30 dias)")
    
    params_todas = {
        'data_inicio': data_inicio.strftime('%Y-%m-%d'),
        'data_fim': data_fim.strftime('%Y-%m-%d'),
        'tipo': 'ambos',
        'status': 'TODOS'
    }
    
    try:
        response = requests.get(f"{BASE_URL}{ENDPOINT}", params=params_todas)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso!")
            print(f"📋 Resumo Todas as Contas:")
            print(f"  - Contas a Pagar: {data['resumo']['total_contas_pagar']}")
            print(f"  - Valor a Pagar: R$ {data['resumo']['valor_total_pagar']}")
            print(f"  - Contas a Receber: {data['resumo']['total_contas_receber']}")
            print(f"  - Valor a Receber: R$ {data['resumo']['valor_total_receber']}")
            
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 5: Teste de validação (sem parâmetros)
    print("\n" + "=" * 60)
    print("📊 TESTE 5: Validação (sem parâmetros obrigatórios)")
    
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
    print("  - status: 'P', 'A', 'C' ou 'TODOS' (padrão: 'A')")
    print("  - incluir_vencidas: 'true' ou 'false' (padrão: 'true')")

if __name__ == "__main__":
    testar_endpoint()
