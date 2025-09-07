#!/usr/bin/env python
"""
Teste para verificar se o estoque está sendo alterado corretamente quando diferentes datas são informadas
"""
import os
import sys
import django
import requests
import json
from datetime import datetime, date

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

def testar_estoque_por_data():
    """Testa se o estoque varia corretamente com datas diferentes"""
    
    print("="*80)
    print("TESTE DE VARIAÇÃO DE ESTOQUE POR DATA")
    print("="*80)
    
    base_url = "http://127.0.0.1:8000/api/estoque-controle"
    
    # Datas para teste - do mais antigo para o mais recente
    datas_teste = [
        '2025-01-01',  # Data inicial do estoque
        '2025-01-15',  # 15 dias após início
        '2025-02-01',  # 1 mês após início
        '2025-03-01',  # 2 meses após início
        '2025-06-01',  # 5 meses após início
        '2025-09-06'   # Data atual (mais movimentações)
    ]
    
    print("🔍 Testando estoque em diferentes datas...")
    print("📝 Usando produto específico para análise detalhada\n")
    
    # Primeiro, vamos encontrar um produto que teve movimentações
    print("1. Buscando produto com movimentações...")
    try:
        response = requests.get(f"{base_url}/produtos_mais_movimentados/?limite=3", timeout=10)
        if response.status_code == 200:
            data = response.json()
            produtos_movimentados = data.get('produtos', [])
            
            if produtos_movimentados:
                produto_teste = produtos_movimentados[0]
                produto_id = produto_teste.get('produto_id')
                nome_produto = produto_teste.get('nome', 'N/A')
                total_movs = produto_teste.get('total_movimentacoes', 0)
                
                print(f"✅ Produto selecionado para teste:")
                print(f"   ID: {produto_id}")
                print(f"   Nome: {nome_produto}")
                print(f"   Total de movimentações: {total_movs}")
                print()
            else:
                print("❌ Nenhum produto com movimentações encontrado")
                return
        else:
            print("❌ Erro ao buscar produtos movimentados")
            return
    except Exception as e:
        print(f"❌ Erro ao buscar produtos: {str(e)}")
        return
    
    # Agora testa o estoque deste produto em cada data
    print("2. Testando estoque do produto em diferentes datas:")
    print("-" * 60)
    
    resultados = []
    
    for i, data_teste in enumerate(datas_teste):
        print(f"📅 Data: {data_teste}")
        
        try:
            url = f"{base_url}/estoque_atual/?produto_id={produto_id}&data={data_teste}"
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                estoque = data.get('estoque', [])
                
                if estoque:
                    produto = estoque[0]
                    quantidade = produto.get('quantidade_atual', 0)
                    valor = produto.get('valor_atual', 0)
                    movs_recentes = produto.get('movimentacoes_recentes', [])
                    
                    print(f"   Quantidade: {quantidade}")
                    print(f"   Valor: R$ {valor:,.2f}")
                    print(f"   Movimentações até esta data: {len(movs_recentes)}")
                    
                    resultados.append({
                        'data': data_teste,
                        'quantidade': float(quantidade),
                        'valor': float(valor),
                        'movimentacoes_count': len(movs_recentes)
                    })
                else:
                    print("   ❌ Produto não encontrado nesta data")
                    resultados.append({
                        'data': data_teste,
                        'quantidade': 0,
                        'valor': 0,
                        'movimentacoes_count': 0
                    })
            else:
                print(f"   ❌ Erro HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Erro: {error_data.get('error', 'N/A')}")
                except:
                    pass
                
                resultados.append({
                    'data': data_teste,
                    'quantidade': None,
                    'valor': None,
                    'movimentacoes_count': None
                })
                
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
            resultados.append({
                'data': data_teste,
                'quantidade': None,
                'valor': None,
                'movimentacoes_count': None
            })
        
        print()
    
    # Análise dos resultados
    print("="*60)
    print("ANÁLISE DOS RESULTADOS")
    print("="*60)
    
    # Filtra resultados válidos
    resultados_validos = [r for r in resultados if r['quantidade'] is not None]
    
    if len(resultados_validos) >= 2:
        print("📊 Comparação entre datas:")
        print()
        
        # Tabela de resultados
        print(f"{'Data':<12} {'Quantidade':<12} {'Valor (R$)':<15} {'Variação Qty':<15} {'Variação Valor':<15}")
        print("-" * 80)
        
        quantidade_anterior = None
        valor_anterior = None
        
        houve_variacao_qty = False
        houve_variacao_valor = False
        
        for resultado in resultados_validos:
            data = resultado['data']
            quantidade = resultado['quantidade']
            valor = resultado['valor']
            
            # Calcula variações
            if quantidade_anterior is not None:
                var_qty = quantidade - quantidade_anterior
                var_valor = valor - valor_anterior
                
                if var_qty != 0:
                    houve_variacao_qty = True
                if var_valor != 0:
                    houve_variacao_valor = True
                
                var_qty_str = f"{var_qty:+.1f}" if var_qty != 0 else "0.0"
                var_valor_str = f"{var_valor:+,.2f}" if var_valor != 0 else "0.00"
            else:
                var_qty_str = "—"
                var_valor_str = "—"
            
            print(f"{data:<12} {quantidade:<12.1f} {valor:<15,.2f} {var_qty_str:<15} {var_valor_str:<15}")
            
            quantidade_anterior = quantidade
            valor_anterior = valor
        
        print("\n📈 Conclusões:")
        
        if houve_variacao_qty:
            print("✅ ESTOQUE VARIA CORRETAMENTE - Quantidades diferentes entre datas")
            
            # Mostra maior e menor quantidade
            quantidades = [r['quantidade'] for r in resultados_validos]
            print(f"   📊 Quantidade mínima: {min(quantidades):.1f}")
            print(f"   📊 Quantidade máxima: {max(quantidades):.1f}")
            print(f"   📊 Variação total: {max(quantidades) - min(quantidades):.1f}")
        else:
            print("⚠️  ESTOQUE NÃO VARIA - Quantidades idênticas em todas as datas")
            print("   Isso pode indicar:")
            print("   • Produto sem movimentações no período")
            print("   • Problema no cálculo por data")
            print("   • Todas as movimentações foram antes de 2025-01-01")
        
        if houve_variacao_valor:
            print("✅ VALORES VARIAM CORRETAMENTE - Valores diferentes entre datas")
            
            # Mostra maior e menor valor
            valores = [r['valor'] for r in resultados_validos]
            print(f"   💰 Valor mínimo: R$ {min(valores):,.2f}")
            print(f"   💰 Valor máximo: R$ {max(valores):,.2f}")
            print(f"   💰 Variação total: R$ {max(valores) - min(valores):,.2f}")
        else:
            print("⚠️  VALORES NÃO VARIAM - Valores idênticos em todas as datas")
    
    else:
        print("❌ Dados insuficientes para análise de variação")
        print(f"   Apenas {len(resultados_validos)} resultado(s) válido(s) de {len(resultados)} teste(s)")
    
    # Teste adicional: comparar estatísticas gerais entre duas datas
    print("\n" + "="*60)
    print("TESTE ADICIONAL: ESTATÍSTICAS GERAIS")
    print("="*60)
    
    datas_comparacao = ['2025-01-01', '2025-09-06']
    print("🔍 Comparando estatísticas gerais entre datas extremas...")
    
    for data in datas_comparacao:
        print(f"\n📅 {data}:")
        try:
            url = f"{base_url}/estoque_atual/?data={data}&limite=50"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data_response = response.json()
                estatisticas = data_response.get('estatisticas', {})
                
                if estatisticas:
                    print(f"   📦 Total de produtos: {estatisticas.get('total_produtos', 0)}")
                    print(f"   ✅ Produtos com estoque: {estatisticas.get('produtos_com_estoque', 0)}")
                    print(f"   💰 Valor total: R$ {estatisticas.get('valor_total_atual', 0):,.2f}")
                else:
                    print("   ❌ Estatísticas não disponíveis")
            else:
                print(f"   ❌ Erro HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    testar_estoque_por_data()
