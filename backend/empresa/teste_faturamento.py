#!/usr/bin/env python
"""
Script para testar o endpoint de faturamento
"""

import requests
import json
from datetime import datetime, timedelta

# Configurações
BASE_URL = "http://127.0.0.1:8000"
ENDPOINT = "/contas/relatorios/faturamento/"

def test_faturamento():
    """Testa o endpoint de faturamento"""
    
    # Definir período de teste (últimos 30 dias)
    data_fim = datetime.now().date()
    data_inicio = data_fim - timedelta(days=30)
    
    # Parâmetros da requisição
    params = {
        'data_inicio': data_inicio.strftime('%Y-%m-%d'),
        'data_fim': data_fim.strftime('%Y-%m-%d')
    }
    
    # URL completa
    url = f"{BASE_URL}{ENDPOINT}"
    
    print(f"🔍 Testando endpoint: {url}")
    print(f"📅 Período: {params['data_inicio']} a {params['data_fim']}")
    print("-" * 60)
    
    try:
        # Fazer requisição
        response = requests.get(url, params=params)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Requisição bem-sucedida!")
            
            # Totais gerais
            totais = data.get('totais_gerais', {})
            print(f"📈 Total de notas: {totais.get('total_quantidade_notas', 0)}")
            print(f"💰 Total valor produtos: R$ {totais.get('total_valor_produtos', 0):,.2f}")
            print(f"💰 Total valor geral: R$ {totais.get('total_valor_geral', 0):,.2f}")
            print(f"💰 Total impostos: R$ {totais.get('total_impostos', 0):,.2f}")
            
            # Resumo por tipo
            resumo_tipo = data.get('resumo_por_tipo', [])
            print(f"\n📋 Resumo por Tipo de Operação:")
            
            for tipo in resumo_tipo:
                print(f"  🔸 {tipo['tipo']}: {tipo['quantidade_notas']} notas")
                print(f"     └─ Valor Total: R$ {tipo['valor_total']:,.2f}")
                print(f"     └─ Impostos: R$ {tipo['impostos']:,.2f}")
            
            # Top fornecedores
            top_fornecedores = data.get('top_fornecedores', [])
            if top_fornecedores:
                print(f"\n🏪 Top Fornecedores (Compras) - Top 5:")
                for i, fornecedor in enumerate(top_fornecedores[:5]):
                    print(f"  {i+1}. {fornecedor['fornecedor']}")
                    print(f"     └─ R$ {fornecedor['valor_total']:,.2f} ({fornecedor['quantidade_notas']} notas)")
            
            # Top clientes
            top_clientes = data.get('top_clientes', [])
            if top_clientes:
                print(f"\n👥 Top Clientes (Vendas + Serviços) - Top 5:")
                for i, cliente in enumerate(top_clientes[:5]):
                    print(f"  {i+1}. {cliente['cliente']} ({cliente['tipo']})")
                    print(f"     └─ R$ {cliente['valor_total']:,.2f} ({cliente['quantidade_notas']} notas)")
            
            # Detalhes das notas
            notas_detalhadas = data.get('notas_detalhadas', {})
            
            print(f"\n📄 Amostras de Notas Fiscais:")
            
            compras = notas_detalhadas.get('compras', [])
            if compras:
                print(f"  💼 Compras (primeiras 3 de {len(compras)}):")
                for i, nf in enumerate(compras[:3]):
                    print(f"    {i+1}. NF {nf['numero_nota']} - {nf['fornecedor']}")
                    print(f"       └─ R$ {nf['valor_total']:,.2f} - {nf['data_emissao']}")
            
            vendas = notas_detalhadas.get('vendas', [])
            if vendas:
                print(f"  💰 Vendas (primeiras 3 de {len(vendas)}):")
                for i, nf in enumerate(vendas[:3]):
                    print(f"    {i+1}. NF {nf['numero_nota']} - {nf['cliente']}")
                    print(f"       └─ R$ {nf['valor_total']:,.2f} - {nf['data']}")
            
            servicos = notas_detalhadas.get('servicos', [])
            if servicos:
                print(f"  🔧 Serviços (primeiras 3 de {len(servicos)}):")
                for i, nf in enumerate(servicos[:3]):
                    print(f"    {i+1}. NF {nf['numero_nota']} - {nf['cliente']}")
                    print(f"       └─ R$ {nf['valor_total']:,.2f} - {nf['data']}")
            
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📝 Detalhes do erro: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"📝 Resposta: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão. Verifique se o servidor Django está rodando.")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_faturamento()
