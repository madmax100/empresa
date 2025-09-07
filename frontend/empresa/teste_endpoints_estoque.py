#!/usr/bin/env python
"""
Script de Teste dos Endpoints de Estoque
========================================

Este script testa os endpoints que serão utilizados pela página
de Estoque Completo para verificar se estão funcionando corretamente.
"""

import requests
import json
from datetime import date, timedelta

def testar_endpoints():
    """Testa todos os endpoints de estoque"""
    base_url = "http://127.0.0.1:8000/contas"
    
    print("🧪 TESTANDO ENDPOINTS DE ESTOQUE")
    print("=" * 50)
    
    # 1. Testar Saldos Atuais
    print("\n1️⃣  Testando Saldos Atuais...")
    try:
        response = requests.get(f"{base_url}/saldos_estoque/?quantidade__gt=0&limit=5")
        if response.status_code == 200:
            data = response.json()
            # Verificar se é lista ou dict
            if isinstance(data, list):
                results = data
                count = len(results)
                total = count
            else:
                results = data.get('results', [])
                count = len(results)
                total = data.get('count', count)
            
            print(f"   ✅ Sucesso: {count} de {total} saldos encontrados")
            
            if count > 0:
                primeiro = results[0]
                produto_nome = primeiro.get('produto', {})
                if isinstance(produto_nome, dict):
                    produto_nome = produto_nome.get('nome', 'N/A')
                else:
                    produto_nome = str(produto_nome)
                print(f"   📦 Exemplo: {produto_nome} - Qtd: {primeiro.get('quantidade', 0)}")
        else:
            print(f"   ❌ Erro {response.status_code}: {response.text[:100]}...")
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
    
    # 2. Testar Movimentações do Dia
    print("\n2️⃣  Testando Movimentações do Dia...")
    data_hoje = date.today().strftime("%Y-%m-%d")
    try:
        response = requests.get(f"{base_url}/movimentacoes_estoque/?data_movimentacao__date={data_hoje}&limit=5")
        if response.status_code == 200:
            data = response.json()
            # Verificar se é lista ou dict
            if isinstance(data, list):
                results = data
                count = len(results)
                total = count
            else:
                results = data.get('results', [])
                count = len(results)
                total = data.get('count', count)
            
            print(f"   ✅ Sucesso: {count} de {total} movimentações de hoje")
            
            if count > 0:
                primeira = results[0]
                produto_nome = primeira.get('produto', {})
                if isinstance(produto_nome, dict):
                    produto_nome = produto_nome.get('nome', 'N/A')
                else:
                    produto_nome = str(produto_nome)
                
                tipo_nome = primeira.get('tipo_movimentacao', {})
                if isinstance(tipo_nome, dict):
                    tipo_nome = tipo_nome.get('nome', 'N/A')
                else:
                    tipo_nome = str(tipo_nome)
                
                print(f"   📋 Exemplo: {produto_nome} - Tipo: {tipo_nome}")
        else:
            print(f"   ❌ Erro {response.status_code}: {response.text[:100]}...")
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
    
    # 3. Testar Movimentações de Janeiro/2025
    print("\n3️⃣  Testando Movimentações de Janeiro/2025...")
    try:
        response = requests.get(f"{base_url}/movimentacoes_estoque/?data_movimentacao__date=2025-01-01&limit=5")
        if response.status_code == 200:
            data = response.json()
            # Verificar se é lista ou dict
            if isinstance(data, list):
                results = data
                count = len(results)
            else:
                results = data.get('results', [])
                count = len(results)
            
            print(f"   ✅ Sucesso: {count} movimentações em 01/01/2025")
            
            if count > 0:
                primeira = results[0]
                produto_nome = primeira.get('produto', {})
                if isinstance(produto_nome, dict):
                    produto_nome = produto_nome.get('nome', 'N/A')
                else:
                    produto_nome = str(produto_nome)
                print(f"   📋 Saldo Inicial: {produto_nome} - Qtd: {primeira.get('quantidade', 0)}")
        else:
            print(f"   ❌ Erro {response.status_code}: {response.text[:100]}...")
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
    
    # 4. Testar Relatório Valor Estoque (pode não funcionar)
    print("\n4️⃣  Testando Relatório Valor Estoque...")
    try:
        response = requests.get(f"{base_url}/relatorio-valor-estoque/?data=2025-08-31")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Sucesso: Relatório de valor disponível")
            print(f"   💰 Valor total: R$ {data.get('valor_total', 0):,.2f}")
        else:
            print(f"   ⚠️  Endpoint não funcional (esperado): {response.status_code}")
            print("   💡 Usando fallback para posições de estoque")
    except Exception as e:
        print(f"   ⚠️  Endpoint não funcional (esperado): {e}")
    
    # 5. Testar Posições de Estoque (fallback)
    print("\n5️⃣  Testando Posições de Estoque (fallback)...")
    try:
        response = requests.get(f"{base_url}/posicoes_estoque/?limit=5")
        if response.status_code == 200:
            data = response.json()
            # Verificar se é lista ou dict
            if isinstance(data, list):
                results = data
                count = len(results)
                total = count
            else:
                results = data.get('results', [])
                count = len(results)
                total = data.get('count', count)
            
            print(f"   ✅ Sucesso: {count} de {total} posições encontradas")
        else:
            print(f"   ❌ Erro {response.status_code}: {response.text[:100]}...")
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
    
    # 6. Estatísticas Gerais
    print("\n📊 ESTATÍSTICAS GERAIS")
    print("-" * 30)
    
    try:
        # Total de produtos
        response = requests.get(f"{base_url}/produtos/?limit=1")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                total_produtos = len(data) if len(data) == 1 else "?"
            else:
                total_produtos = data.get('count', 0)
            print(f"   📦 Total de produtos cadastrados: {total_produtos}")
    except Exception:
        print(f"   📦 Total de produtos: Erro ao consultar")
    
    try:
        # Total de saldos
        response = requests.get(f"{base_url}/saldos_estoque/?limit=1")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                total_saldos = len(data) if len(data) == 1 else "?"
            else:
                total_saldos = data.get('count', 0)
            print(f"   💰 Total de saldos: {total_saldos}")
    except Exception:
        print(f"   💰 Total de saldos: Erro ao consultar")
    
    try:
        # Total de movimentações
        response = requests.get(f"{base_url}/movimentacoes_estoque/?limit=1")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                total_movs = len(data) if len(data) == 1 else "?"
            else:
                total_movs = data.get('count', 0)
            print(f"   📋 Total de movimentações: {total_movs}")
    except Exception:
        print(f"   📋 Total de movimentações: Erro ao consultar")
    except:
        pass
    
    print("\n🎯 TESTE CONCLUÍDO!")
    print("\nPróximos passos:")
    print("1. Abra o frontend: http://localhost:5173/financeiro/estoque-completo")
    print("2. Teste todas as 3 abas")
    print("3. Verifique se os dados estão sendo exibidos corretamente")

if __name__ == "__main__":
    testar_endpoints()
