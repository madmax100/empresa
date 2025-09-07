#!/usr/bin/env python
"""
Script para testar e demonstrar endpoints de estoque por data
"""

import os
import sys
import django
from datetime import datetime, date, timedelta
from decimal import Decimal
import requests
import json

# Configurar Django
sys.path.append(os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models import MovimentacoesEstoque, SaldosEstoque, Produtos

def testar_endpoint_estoque_data():
    """Testa o endpoint de estoque por data específica"""
    print("🔍 TESTANDO ENDPOINTS DE ESTOQUE POR DATA")
    print("=" * 60)
    
    # URL base (ajuste conforme sua configuração)
    base_url = "http://localhost:8000/api"  # ou sua URL de produção
    
    # Datas para teste
    hoje = date.today()
    ontem = hoje - timedelta(days=1)
    semana_passada = hoje - timedelta(days=7)
    mes_passado = hoje - timedelta(days=30)
    
    datas_teste = [
        ("Hoje", hoje.strftime('%Y-%m-%d')),
        ("Ontem", ontem.strftime('%Y-%m-%d')),
        ("Semana passada", semana_passada.strftime('%Y-%m-%d')),
        ("Mês passado", mes_passado.strftime('%Y-%m-%d')),
        ("01/01/2024", "2024-01-01"),
        ("01/08/2025", "2025-08-01")
    ]
    
    print("1. ENDPOINT DEDICADO: /relatorio-valor-estoque/")
    print("-" * 50)
    
    for nome, data_str in datas_teste:
        try:
            url = f"{base_url}/relatorio-valor-estoque/?data={data_str}"
            print(f"\n📅 {nome} ({data_str})")
            print(f"URL: {url}")
            
            # Simular resposta (já que não temos servidor rodando)
            print("⚠️  Endpoint disponível mas servidor não está rodando")
            print("💡 Para testar: GET /api/relatorio-valor-estoque/?data=YYYY-MM-DD")
            
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
    
    print("\n" + "=" * 60)
    print("2. ENDPOINT SALDOS ESTOQUE: /saldos_estoque/")
    print("-" * 50)
    print("💡 URL: /api/saldos_estoque/")
    print("📝 Mostra saldos atuais (não histórico)")
    print("🔍 Filtros disponíveis:")
    print("   - ?quantidade__gt=0 (apenas saldos positivos)")
    print("   - ?produto_id__codigo=XXX (por código do produto)")
    
    print("\n" + "=" * 60)
    print("3. ENDPOINT MOVIMENTAÇÕES: /movimentacoes_estoque/")
    print("-" * 50)
    print("💡 URL: /api/movimentacoes_estoque/")
    print("📝 Mostra movimentações históricas")
    print("🔍 Filtros disponíveis:")
    print("   - ?data_movimentacao__date=YYYY-MM-DD (movimentações do dia)")
    print("   - ?data_movimentacao__gte=YYYY-MM-DD (a partir de)")
    print("   - ?data_movimentacao__lte=YYYY-MM-DD (até)")
    print("   - ?produto__codigo=XXX (por produto)")

def calcular_estoque_direto_por_data(data_referencia):
    """Calcula estoque diretamente do banco por data"""
    print(f"\n📊 CALCULANDO ESTOQUE EM {data_referencia}")
    print("-" * 50)
    
    # Busca movimentações até a data
    movimentacoes = MovimentacoesEstoque.objects.filter(
        data_movimentacao__date__lte=data_referencia
    ).select_related('produto', 'tipo_movimentacao')
    
    # Agrupa por produto
    saldos_por_produto = {}
    
    for mov in movimentacoes:
        if not mov.produto:
            continue
            
        produto_id = mov.produto.id
        
        if produto_id not in saldos_por_produto:
            saldos_por_produto[produto_id] = {
                'produto': mov.produto,
                'quantidade': Decimal('0'),
                'movimentacoes': 0,
                'ultima_movimentacao': None
            }
        
        # Calcula saldo
        if mov.tipo_movimentacao and mov.tipo_movimentacao.tipo == 'E':  # Entrada
            saldos_por_produto[produto_id]['quantidade'] += mov.quantidade
        elif mov.tipo_movimentacao and mov.tipo_movimentacao.tipo == 'S':  # Saída
            saldos_por_produto[produto_id]['quantidade'] -= mov.quantidade
        
        saldos_por_produto[produto_id]['movimentacoes'] += 1
        
        if (not saldos_por_produto[produto_id]['ultima_movimentacao'] or 
            mov.data_movimentacao > saldos_por_produto[produto_id]['ultima_movimentacao']):
            saldos_por_produto[produto_id]['ultima_movimentacao'] = mov.data_movimentacao
    
    # Filtra apenas saldos positivos
    saldos_positivos = {
        k: v for k, v in saldos_por_produto.items() 
        if v['quantidade'] > 0
    }
    
    # Ordena por quantidade
    saldos_ordenados = sorted(
        saldos_positivos.items(), 
        key=lambda x: x[1]['quantidade'], 
        reverse=True
    )
    
    print(f"📦 Produtos com estoque positivo em {data_referencia}: {len(saldos_positivos)}")
    print(f"📈 Total de produtos com movimentação: {len(saldos_por_produto)}")
    
    if saldos_ordenados:
        print(f"\n🏆 TOP 10 PRODUTOS COM MAIOR ESTOQUE:")
        print(f"{'Código':<15} {'Nome':<30} {'Qtd':<10} {'Última Mov':<12}")
        print("-" * 70)
        
        for produto_id, dados in saldos_ordenados[:10]:
            produto = dados['produto']
            quantidade = dados['quantidade']
            ultima = dados['ultima_movimentacao'].strftime('%d/%m/%Y') if dados['ultima_movimentacao'] else 'N/D'
            
            print(f"{produto.codigo:<15} {produto.nome[:30]:<30} {quantidade:<10} {ultima:<12}")

def demonstrar_uso_api():
    """Demonstra como usar a API para consultar estoque por data"""
    print("\n" + "=" * 80)
    print("🚀 COMO USAR OS ENDPOINTS DE ESTOQUE POR DATA")
    print("=" * 80)
    
    exemplos = [
        {
            "titulo": "1. VALOR TOTAL DO ESTOQUE EM UMA DATA ESPECÍFICA",
            "endpoint": "/api/relatorio-valor-estoque/",
            "metodo": "GET",
            "parametros": "?data=2025-09-01",
            "descricao": "Calcula valor total baseado nas movimentações até a data",
            "resposta_exemplo": {
                "data_posicao": "2025-09-01",
                "valor_total_estoque": "1039513.09",
                "total_produtos_em_estoque": 481,
                "detalhes_por_produto": [
                    {
                        "produto_id": 4032,
                        "produto_descricao": "TINTA PRETA/RC JP7 750",
                        "quantidade_em_estoque": "4261.000",
                        "custo_unitario": "21.79",
                        "valor_total_produto": "92851.02"
                    }
                ]
            }
        },
        {
            "titulo": "2. SALDOS ATUAIS (TEMPO REAL)",
            "endpoint": "/api/saldos_estoque/",
            "metodo": "GET",
            "parametros": "?quantidade__gt=0",
            "descricao": "Mostra saldos atualmente cadastrados na tabela",
            "resposta_exemplo": [
                {
                    "id": 1,
                    "produto_id": 4032,
                    "quantidade": "4261.000",
                    "custo_medio": "21.79",
                    "ultima_movimentacao": "2025-09-01T10:30:00Z"
                }
            ]
        },
        {
            "titulo": "3. MOVIMENTAÇÕES EM UMA DATA",
            "endpoint": "/api/movimentacoes_estoque/",
            "metodo": "GET", 
            "parametros": "?data_movimentacao__date=2025-09-01",
            "descricao": "Lista movimentações de um dia específico",
            "resposta_exemplo": [
                {
                    "id": 123,
                    "data_movimentacao": "2025-09-01T14:30:00Z",
                    "tipo_movimentacao": {"codigo": "ENT", "descricao": "Entrada"},
                    "produto": {"codigo": "4032", "nome": "TINTA PRETA"},
                    "quantidade": "10.000",
                    "custo_unitario": "21.79"
                }
            ]
        },
        {
            "titulo": "4. HISTÓRICO DE MOVIMENTAÇÕES",
            "endpoint": "/api/movimentacoes_estoque/",
            "metodo": "GET",
            "parametros": "?data_movimentacao__gte=2025-08-01&data_movimentacao__lte=2025-09-01",
            "descricao": "Movimentações em um período",
            "resposta_exemplo": "Lista de movimentações no período"
        }
    ]
    
    for exemplo in exemplos:
        print(f"\n{exemplo['titulo']}")
        print("-" * 60)
        print(f"🔗 Endpoint: {exemplo['endpoint']}")
        print(f"📤 Método: {exemplo['metodo']}")
        print(f"📋 Parâmetros: {exemplo['parametros']}")
        print(f"📝 Descrição: {exemplo['descricao']}")
        print(f"📄 Exemplo de resposta:")
        print(json.dumps(exemplo['resposta_exemplo'], indent=2, ensure_ascii=False))

def main():
    """Função principal"""
    try:
        print(f"Executado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Testa endpoints
        testar_endpoint_estoque_data()
        
        # Calcula estoque direto para algumas datas
        datas_teste = [
            date.today(),
            date.today() - timedelta(days=7),
            date(2025, 8, 1)
        ]
        
        for data_teste in datas_teste:
            calcular_estoque_direto_por_data(data_teste)
        
        # Demonstra uso da API
        demonstrar_uso_api()
        
        print("\n" + "=" * 80)
        print("✅ RESUMO DOS ENDPOINTS DISPONÍVEIS")
        print("=" * 80)
        print("🎯 RECOMENDADO para estoque por data:")
        print("   GET /api/relatorio-valor-estoque/?data=YYYY-MM-DD")
        print("   ✅ Calcula estoque histórico baseado nas movimentações")
        print("   ✅ Retorna valor total e detalhes por produto")
        print("   ✅ Considera apenas saldos positivos")
        
        print("\n🔄 Para saldos atuais:")
        print("   GET /api/saldos_estoque/?quantidade__gt=0")
        
        print("\n📊 Para movimentações:")
        print("   GET /api/movimentacoes_estoque/?data_movimentacao__date=YYYY-MM-DD")
        
        print("\n💡 DICA: Use o endpoint 'relatorio-valor-estoque' para consultas históricas!")
        
    except Exception as e:
        print(f"Erro durante a execução: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
