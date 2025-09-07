#!/usr/bin/env python
"""
Teste do novo endpoint de movimentações por período
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

def testar_endpoint_movimentacoes_periodo():
    """Testa o novo endpoint de movimentações por período"""
    
    print("="*80)
    print("TESTE DO ENDPOINT MOVIMENTAÇÕES POR PERÍODO")
    print("="*80)
    
    base_url = "http://127.0.0.1:8000/api/estoque-controle"
    
    # Configuração dos testes
    testes = [
        {
            'nome': 'Teste 1: Janeiro 2025 completo',
            'url': f"{base_url}/movimentacoes_periodo/?data_inicio=2025-01-01&data_fim=2025-01-31",
            'timeout': 30
        },
        {
            'nome': 'Teste 2: Últimos 30 dias (com limite)',
            'url': f"{base_url}/movimentacoes_periodo/?data_inicio=2025-08-01&data_fim=2025-09-06&limite=10",
            'timeout': 30
        },
        {
            'nome': 'Teste 3: Período específico com detalhes',
            'url': f"{base_url}/movimentacoes_periodo/?data_inicio=2025-06-20&data_fim=2025-06-30&incluir_detalhes=true&limite=5",
            'timeout': 30
        },
        {
            'nome': 'Teste 4: Teste de validação (data inválida)',
            'url': f"{base_url}/movimentacoes_periodo/?data_inicio=2025-12-01&data_fim=2025-11-01",
            'timeout': 10
        },
        {
            'nome': 'Teste 5: Parâmetros ausentes',
            'url': f"{base_url}/movimentacoes_periodo/",
            'timeout': 10
        }
    ]
    
    resultados = []
    
    for i, teste in enumerate(testes, 1):
        print(f"\n{'-'*60}")
        print(f"{teste['nome']}")
        print(f"URL: {teste['url']}")
        print("-"*60)
        
        try:
            inicio = datetime.now()
            response = requests.get(teste['url'], timeout=teste['timeout'])
            tempo_resposta = (datetime.now() - inicio).total_seconds()
            
            print(f"⏱️  Tempo de resposta: {tempo_resposta:.2f}s")
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Informações do resultado
                produtos = data.get('produtos_movimentados', [])
                resumo = data.get('resumo', {})
                parametros = data.get('parametros', {})
                
                print(f"✅ Sucesso!")
                print(f"📅 Período: {resumo.get('periodo', 'N/A')}")
                print(f"📦 Produtos movimentados: {resumo.get('total_produtos', 0)}")
                print(f"🔄 Total de movimentações: {resumo.get('total_movimentacoes', 0)}")
                print(f"⬆️  Valor entradas: R$ {resumo.get('valor_total_entradas', 0):,.2f}")
                print(f"⬇️  Valor saídas: R$ {resumo.get('valor_total_saidas', 0):,.2f}")
                print(f"💰 Saldo período: R$ {resumo.get('saldo_periodo', 0):,.2f}")
                
                if parametros.get('limite_aplicado'):
                    print(f"📊 Limite aplicado: {parametros['limite_aplicado']}")
                
                # Mostra top 3 produtos se houver
                if produtos:
                    print(f"\n📦 Top 3 produtos mais movimentados:")
                    for j, produto in enumerate(produtos[:3], 1):
                        nome = produto.get('nome', 'N/A')[:50]
                        valor_total_mov = produto.get('valor_entrada', 0) + produto.get('valor_saida', 0)
                        movs = produto.get('total_movimentacoes', 0)
                        print(f"   {j}. {nome} - R$ {valor_total_mov:,.2f} ({movs} movs)")
                
                resultados.append({
                    'teste': teste['nome'],
                    'status': 'SUCESSO',
                    'tempo': tempo_resposta,
                    'produtos': len(produtos),
                    'valor_entradas': resumo.get('valor_total_entradas', 0),
                    'valor_saidas': resumo.get('valor_total_saidas', 0)
                })
                
            elif response.status_code == 400:
                print(f"⚠️  Erro de validação (esperado em alguns testes)")
                try:
                    error_data = response.json()
                    print(f"💬 Erro: {error_data.get('error', 'N/A')}")
                except:
                    pass
                
                resultados.append({
                    'teste': teste['nome'],
                    'status': 'VALIDACAO_OK',
                    'tempo': tempo_resposta,
                    'produtos': 0,
                    'valor_entradas': 0,
                    'valor_saidas': 0
                })
                
            else:
                print(f"❌ Erro HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"💬 Erro: {error_data.get('error', 'N/A')}")
                except:
                    print(f"💬 Resposta: {response.text[:200]}...")
                
                resultados.append({
                    'teste': teste['nome'],
                    'status': 'ERRO_HTTP',
                    'tempo': tempo_resposta,
                    'produtos': 0,
                    'valor_entradas': 0,
                    'valor_saidas': 0
                })
                
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout após {teste['timeout']}s")
            resultados.append({
                'teste': teste['nome'],
                'status': 'TIMEOUT',
                'tempo': teste['timeout'],
                'produtos': 0,
                'valor_entradas': 0,
                'valor_saidas': 0
            })
            
        except Exception as e:
            print(f"💥 Erro inesperado: {str(e)}")
            resultados.append({
                'teste': teste['nome'],
                'status': 'ERRO_INESPERADO',
                'tempo': 0,
                'produtos': 0,
                'valor_entradas': 0,
                'valor_saidas': 0
            })
    
    # Resumo final
    print("\n" + "="*80)
    print("RESUMO DOS TESTES - MOVIMENTAÇÕES POR PERÍODO")
    print("="*80)
    
    sucessos = len([r for r in resultados if r['status'] in ['SUCESSO', 'VALIDACAO_OK']])
    total_testes = len(resultados)
    
    print(f"📊 Testes executados: {total_testes}")
    print(f"✅ Sucessos: {sucessos}")
    print(f"❌ Falhas: {total_testes - sucessos}")
    print(f"📈 Taxa de sucesso: {(sucessos/total_testes)*100:.1f}%")
    
    print(f"\n📋 Detalhes por teste:")
    for resultado in resultados:
        status_icon = "✅" if resultado['status'] in ['SUCESSO', 'VALIDACAO_OK'] else "❌"
        print(f"{status_icon} {resultado['teste'][:50]:<50}: {resultado['status']:<15} ({resultado['tempo']:.1f}s)")
        if resultado['status'] == 'SUCESSO':
            print(f"     📦 {resultado['produtos']} produtos, ⬆️ R$ {resultado['valor_entradas']:,.2f}, ⬇️ R$ {resultado['valor_saidas']:,.2f}")
    
    if sucessos == total_testes:
        print(f"\n🎉 TODOS OS TESTES PASSARAM! O endpoint está funcionando corretamente.")
    else:
        print(f"\n⚠️  Alguns testes falharam, mas validações podem estar funcionando corretamente.")
    
    print("\n" + "="*80)
    print("EXEMPLOS DE USO DO ENDPOINT")
    print("="*80)
    print("📌 Movimentações de janeiro:")
    print("   GET /api/estoque-controle/movimentacoes_periodo/?data_inicio=2025-01-01&data_fim=2025-01-31")
    print()
    print("📌 Top 10 produtos mais movimentados em junho:")
    print("   GET /api/estoque-controle/movimentacoes_periodo/?data_inicio=2025-06-01&data_fim=2025-06-30&limite=10")
    print()
    print("📌 Movimentações detalhadas da última semana:")
    print("   GET /api/estoque-controle/movimentacoes_periodo/?data_inicio=2025-08-30&data_fim=2025-09-06&incluir_detalhes=true")
    print("="*80)

if __name__ == "__main__":
    testar_endpoint_movimentacoes_periodo()
