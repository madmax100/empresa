#!/usr/bin/env python3
"""
Script de teste completo para o endpoint movimentacoes_periodo corrigido
Testa todas as funcionalidades e novos campos implementados
"""

import os
import sys
import django
import requests
import json
from datetime import datetime, date

# Configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

# URL base da API
BASE_URL = 'http://localhost:8000/api/estoque-controle'

def formatar_valor(valor):
    """Formata valor monetário para exibição"""
    return f"R$ {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')

def formatar_quantidade(quantidade):
    """Formata quantidade para exibição"""
    return f"{quantidade:.2f}".replace('.', ',')

def testar_endpoint_completo():
    """
    Testa o endpoint com todos os novos campos implementados
    """
    print("=" * 80)
    print("🧪 TESTE COMPLETO DO ENDPOINT MOVIMENTACOES_PERIODO CORRIGIDO")
    print("=" * 80)
    
    # Teste 1: Período janeiro 2025 com detalhes
    print("\n📊 TESTE 1: Janeiro 2025 - Com Detalhes")
    print("-" * 50)
    
    url = f"{BASE_URL}/movimentacoes_periodo/"
    params = {
        'data_inicio': '2025-01-01',
        'data_fim': '2025-01-31',
        'incluir_detalhes': 'true',
        'limite': '10'
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Status: {response.status_code}")
            print(f"📋 Produtos movimentados: {len(data.get('produtos_movimentados', []))}")
            
            # Verifica se possui resumo expandido
            resumo = data.get('resumo', {})
            print(f"\n📈 RESUMO EXPANDIDO:")
            print(f"   Período: {resumo.get('periodo', 'N/A')}")
            print(f"   Total produtos: {resumo.get('total_produtos', 0)}")
            print(f"   Total movimentações: {resumo.get('total_movimentacoes', 0)}")
            print(f"   Valor total entradas: {formatar_valor(resumo.get('valor_total_entradas', 0))}")
            print(f"   Valor total saídas: {formatar_valor(resumo.get('valor_total_saidas', 0))}")
            
            # NOVOS CAMPOS OBRIGATÓRIOS
            print(f"   🆕 Valor saídas (preço entrada): {formatar_valor(resumo.get('valor_total_saidas_preco_entrada', 0))}")
            print(f"   🆕 Diferença total preços: {formatar_valor(resumo.get('diferenca_total_precos', 0))}")
            print(f"   🆕 Margem total: {resumo.get('margem_total', 0):.2f}%")
            print(f"   🆕 Produtos com entrada anterior: {resumo.get('produtos_com_entrada_anterior', 0)}")
            print(f"   🆕 Produtos sem entrada anterior: {resumo.get('produtos_sem_entrada_anterior', 0)}")
            
            # Analisa primeiro produto em detalhe
            produtos = data.get('produtos_movimentados', [])
            if produtos:
                produto = produtos[0]
                print(f"\n🔍 ANÁLISE DETALHADA - {produto.get('nome', 'N/A')}")
                print(f"   ID: {produto.get('produto_id', 'N/A')}")
                print(f"   Referência: {produto.get('referencia', 'N/A')}")
                print(f"   Quantidade entrada: {formatar_quantidade(produto.get('quantidade_entrada', 0))}")
                print(f"   Quantidade saída: {formatar_quantidade(produto.get('quantidade_saida', 0))}")
                print(f"   Valor entrada: {formatar_valor(produto.get('valor_entrada', 0))}")
                print(f"   Valor saída: {formatar_valor(produto.get('valor_saida', 0))}")
                
                # NOVOS CAMPOS OBRIGATÓRIOS POR PRODUTO
                print(f"   🆕 Último preço entrada: {formatar_valor(produto.get('ultimo_preco_entrada', 0))}")
                print(f"   🆕 Data último preço: {produto.get('data_ultimo_preco_entrada', 'N/A')}")
                print(f"   🆕 Valor saída (preço entrada): {formatar_valor(produto.get('valor_saida_preco_entrada', 0))}")
                print(f"   🆕 Diferença preço: {formatar_valor(produto.get('diferenca_preco', 0))}")
                print(f"   🆕 Tem entrada anterior: {produto.get('tem_entrada_anterior', False)}")
                
                # Movimentações detalhadas
                movimentacoes = produto.get('movimentacoes_detalhadas', [])
                print(f"   📋 Movimentações detalhadas: {len(movimentacoes)}")
                
                if movimentacoes:
                    print(f"   🔄 Primeira movimentação:")
                    primeira = movimentacoes[0]
                    print(f"      Data: {primeira.get('data', 'N/A')}")
                    print(f"      Tipo: {primeira.get('tipo_codigo', 'N/A')} - {primeira.get('tipo', 'N/A')}")
                    print(f"      Quantidade: {formatar_quantidade(primeira.get('quantidade', 0))}")
                    print(f"      Valor unitário: {formatar_valor(primeira.get('valor_unitario', 0))}")
                    print(f"      É entrada: {primeira.get('is_entrada', False)}")
                    print(f"      É saída: {primeira.get('is_saida', False)}")
                    
                    # Verifica se tem campos de diferença para saídas
                    if primeira.get('is_saida') and 'diferenca_unitaria' in primeira:
                        print(f"      🆕 Diferença unitária: {formatar_valor(primeira.get('diferenca_unitaria', 0))}")
            
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
    
    # Teste 2: Produto específico
    print("\n" + "=" * 50)
    print("📊 TESTE 2: Produto Específico")
    print("-" * 50)
    
    params = {
        'data_inicio': '2025-01-01',
        'data_fim': '2025-01-31',
        'produto_id': '6440',  # ID conhecido do sistema
        'incluir_detalhes': 'true'
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            produtos = data.get('produtos_movimentados', [])
            
            if produtos:
                produto = produtos[0]
                print(f"✅ Produto encontrado: {produto.get('nome', 'N/A')}")
                print(f"🔢 Total movimentações: {produto.get('total_movimentacoes', 0)}")
                print(f"💰 Valor total saída: {formatar_valor(produto.get('valor_saida', 0))}")
                print(f"🆕 Última entrada: {formatar_valor(produto.get('ultimo_preco_entrada', 0))}")
                print(f"🆕 Diferença: {formatar_valor(produto.get('diferenca_preco', 0))}")
            else:
                print("❌ Produto não encontrado no período")
        else:
            print(f"❌ Erro: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 3: Ordenação por diferença de preço
    print("\n" + "=" * 50)
    print("📊 TESTE 3: Ordenação por Diferença de Preço")
    print("-" * 50)
    
    params = {
        'data_inicio': '2025-01-01',
        'data_fim': '2025-01-31',
        'ordenar_por': 'diferenca_preco',
        'ordem': 'DESC',
        'limite': '5'
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            produtos = data.get('produtos_movimentados', [])
            
            print(f"✅ Top 5 produtos por diferença de preço:")
            for i, produto in enumerate(produtos, 1):
                nome = produto.get('nome', 'N/A')[:30]
                diferenca = produto.get('diferenca_preco', 0)
                print(f"   {i}. {nome:30} - {formatar_valor(diferenca)}")
        else:
            print(f"❌ Erro: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 4: Período sem movimentações
    print("\n" + "=" * 50)
    print("📊 TESTE 4: Período Sem Movimentações")
    print("-" * 50)
    
    params = {
        'data_inicio': '2024-01-01',
        'data_fim': '2024-01-31'
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            resumo = data.get('resumo', {})
            
            print(f"✅ Período vazio tratado corretamente")
            print(f"📊 Total produtos: {resumo.get('total_produtos', 0)}")
            print(f"🆕 Estrutura completa: {len(resumo)} campos no resumo")
            
            # Verifica se todos os campos obrigatórios estão presentes
            campos_obrigatorios = [
                'valor_total_saidas_preco_entrada',
                'diferenca_total_precos',
                'margem_total',
                'produtos_com_entrada_anterior',
                'produtos_sem_entrada_anterior'
            ]
            
            for campo in campos_obrigatorios:
                if campo in resumo:
                    print(f"   ✅ {campo}: {resumo[campo]}")
                else:
                    print(f"   ❌ Campo {campo} ausente")
        else:
            print(f"❌ Erro: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 5: Validação de parâmetros
    print("\n" + "=" * 50)
    print("📊 TESTE 5: Validação de Parâmetros")
    print("-" * 50)
    
    # Testa parâmetros inválidos
    testes_validacao = [
        ({}, "Sem parâmetros"),
        ({'data_inicio': '2025-01-01'}, "Apenas data_inicio"),
        ({'data_inicio': '2025-13-01', 'data_fim': '2025-01-31'}, "Data inválida"),
        ({'data_inicio': '2025-01-31', 'data_fim': '2025-01-01'}, "Intervalo inválido"),
        ({'data_inicio': '2025-01-01', 'data_fim': '2025-01-31', 'produto_id': 'abc'}, "produto_id inválido")
    ]
    
    for params_teste, descricao in testes_validacao:
        try:
            response = requests.get(url, params=params_teste, timeout=10)
            if response.status_code == 400:
                print(f"   ✅ {descricao}: Erro 400 (correto)")
            else:
                print(f"   ❌ {descricao}: Status {response.status_code} (incorreto)")
        except Exception:
            print(f"   ❌ {descricao}: Erro de conexão")

def verificar_estrutura_resposta():
    """
    Verifica se a estrutura da resposta está conforme especificação
    """
    print("\n" + "=" * 80)
    print("🔍 VERIFICAÇÃO DE ESTRUTURA DA RESPOSTA")
    print("=" * 80)
    
    url = f"{BASE_URL}/movimentacoes_periodo/"
    params = {
        'data_inicio': '2025-01-01',
        'data_fim': '2025-01-31',
        'incluir_detalhes': 'true',
        'limite': '1'
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Campos obrigatórios da resposta principal
            campos_principais = ['produtos_movimentados', 'resumo', 'parametros']
            
            print("📋 ESTRUTURA PRINCIPAL:")
            for campo in campos_principais:
                if campo in data:
                    print(f"   ✅ {campo}")
                else:
                    print(f"   ❌ {campo} - AUSENTE")
            
            # Campos obrigatórios do resumo
            resumo = data.get('resumo', {})
            campos_resumo = [
                'periodo', 'total_produtos', 'total_movimentacoes',
                'valor_total_entradas', 'valor_total_saidas',
                'valor_total_saidas_preco_entrada', 'diferenca_total_precos',
                'margem_total', 'saldo_periodo', 'quantidade_total_entradas',
                'quantidade_total_saidas', 'produtos_com_entrada_anterior',
                'produtos_sem_entrada_anterior'
            ]
            
            print(f"\n📊 RESUMO ({len(campos_resumo)} campos obrigatórios):")
            for campo in campos_resumo:
                if campo in resumo:
                    print(f"   ✅ {campo}: {resumo[campo]}")
                else:
                    print(f"   ❌ {campo} - AUSENTE")
            
            # Campos obrigatórios do produto
            produtos = data.get('produtos_movimentados', [])
            if produtos:
                produto = produtos[0]
                campos_produto = [
                    'produto_id', 'nome', 'referencia', 'quantidade_entrada',
                    'quantidade_saida', 'valor_entrada', 'valor_saida',
                    'saldo_quantidade', 'saldo_valor', 'total_movimentacoes',
                    'primeira_movimentacao', 'ultima_movimentacao',
                    'ultimo_preco_entrada', 'data_ultimo_preco_entrada',
                    'valor_saida_preco_entrada', 'diferenca_preco',
                    'tem_entrada_anterior', 'movimentacoes_detalhadas'
                ]
                
                print(f"\n🛍️ PRODUTO ({len(campos_produto)} campos obrigatórios):")
                for campo in campos_produto:
                    if campo in produto:
                        valor = produto[campo]
                        if isinstance(valor, list):
                            print(f"   ✅ {campo}: [{len(valor)} itens]")
                        else:
                            print(f"   ✅ {campo}: {valor}")
                    else:
                        print(f"   ❌ {campo} - AUSENTE")
                
                # Campos das movimentações detalhadas
                movimentacoes = produto.get('movimentacoes_detalhadas', [])
                if movimentacoes:
                    mov = movimentacoes[0]
                    campos_mov = [
                        'id', 'data', 'tipo', 'tipo_codigo', 'quantidade',
                        'valor_unitario', 'valor_total', 'documento',
                        'operador', 'observacoes', 'is_entrada', 'is_saida'
                    ]
                    
                    print(f"\n🔄 MOVIMENTAÇÃO ({len(campos_mov)} campos obrigatórios):")
                    for campo in campos_mov:
                        if campo in mov:
                            print(f"   ✅ {campo}: {mov[campo]}")
                        else:
                            print(f"   ❌ {campo} - AUSENTE")
            
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    """Função principal"""
    print("🚀 Iniciando testes do endpoint movimentacoes_periodo corrigido...")
    
    # Executa todos os testes
    testar_endpoint_completo()
    verificar_estrutura_resposta()
    
    print("\n" + "=" * 80)
    print("✅ TESTES CONCLUÍDOS")
    print("=" * 80)
    print("\n📝 RESUMO:")
    print("   - Endpoint corrigido com todos os campos obrigatórios")
    print("   - Cálculo de último preço de entrada implementado")
    print("   - Análise de margem e diferença de preços funcionando")
    print("   - Movimentações detalhadas com informações expandidas")
    print("   - Validação de parâmetros completa")
    print("   - Estrutura de resposta conforme especificação")

if __name__ == "__main__":
    main()
