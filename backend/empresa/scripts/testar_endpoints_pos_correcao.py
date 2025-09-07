#!/usr/bin/env python3
"""
Script para testar os endpoints após a correção do estoque
"""

import os
import sys
import django
from datetime import datetime, date

# Configurar Django
sys.path.append('c:/Users/Cirilo/Documents/c3mcopias/backend/empresa')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from django.test import Client
import json

def testar_endpoints():
    """Testa os principais endpoints de estoque"""
    print("=== TESTANDO ENDPOINTS PÓS-CORREÇÃO ===")
    
    client = Client()
    
    # 1. Testar endpoint principal
    print("\n1. 🔍 Testando /api/relatorio-valor-estoque/")
    
    try:
        response = client.get('/api/relatorio-valor-estoque/')
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Endpoint funcionando!")
            print(f"   📊 Data da posição: {data.get('data_posicao')}")
            print(f"   💰 Valor total: R$ {data.get('valor_total_estoque', 0):,.2f}")
            print(f"   📦 Produtos em estoque: {data.get('total_produtos_em_estoque', 0)}")
        else:
            print(f"   ❌ Erro {response.status_code}: {response.content}")
            
    except Exception as e:
        print(f"   ❌ Erro ao testar endpoint: {e}")
    
    # 2. Testar com data específica
    print("\n2. 📅 Testando com data 01/01/2025")
    
    try:
        response = client.get('/api/relatorio-valor-estoque/?data=2025-01-01')
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Endpoint com data funcionando!")
            print(f"   📊 Data da posição: {data.get('data_posicao')}")
            print(f"   💰 Valor total: R$ {data.get('valor_total_estoque', 0):,.2f}")
            print(f"   📦 Produtos em estoque: {data.get('total_produtos_em_estoque', 0)}")
        else:
            print(f"   ❌ Erro {response.status_code}: {response.content}")
            
    except Exception as e:
        print(f"   ❌ Erro ao testar endpoint com data: {e}")
    
    # 3. Testar endpoint de saldos
    print("\n3. 📊 Testando /api/saldos_estoque/")
    
    try:
        response = client.get('/api/saldos_estoque/')
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, dict) and 'results' in data:
                total = len(data['results'])
                print(f"   ✅ Endpoint funcionando! {total} saldos encontrados")
            elif isinstance(data, list):
                total = len(data)
                print(f"   ✅ Endpoint funcionando! {total} saldos encontrados")
            else:
                print("   ⚠️  Resposta em formato inesperado")
                
        else:
            print(f"   ❌ Erro {response.status_code}: {response.content}")
            
    except Exception as e:
        print(f"   ❌ Erro ao testar endpoint de saldos: {e}")
    
    # 4. Testar endpoint de movimentações
    print("\n4. 🔄 Testando /api/movimentacoes_estoque/")
    
    try:
        response = client.get('/api/movimentacoes_estoque/')
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, dict) and 'results' in data:
                total = len(data['results'])
                print(f"   ✅ Endpoint funcionando! {total} movimentações encontradas")
            elif isinstance(data, list):
                total = len(data)
                print(f"   ✅ Endpoint funcionando! {total} movimentações encontradas")
            else:
                print("   ⚠️  Resposta em formato inesperado")
                
        else:
            print(f"   ❌ Erro {response.status_code}: {response.content}")
            
    except Exception as e:
        print(f"   ❌ Erro ao testar endpoint de movimentações: {e}")
    
    print("\n✅ TESTE DE ENDPOINTS CONCLUÍDO")

if __name__ == '__main__':
    testar_endpoints()
