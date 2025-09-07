#!/usr/bin/env python
"""
Teste específico para o endpoint estoque_atual corrigido
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

def testar_endpoint_corrigido():
    """Testa o endpoint estoque_atual com as correções implementadas"""
    
    print("="*80)
    print("TESTE DO ENDPOINT ESTOQUE_ATUAL CORRIGIDO")
    print("="*80)
    
    base_url = "http://127.0.0.1:8000/api/estoque-controle"
    
    # Configuração dos testes
    testes = [
        {
            'nome': 'Teste 1: Produto específico (ID=10)',
            'url': f"{base_url}/estoque_atual/?produto_id=10",
            'timeout': 10
        },
        {
            'nome': 'Teste 2: Primeiros 50 produtos',
            'url': f"{base_url}/estoque_atual/?limite=50",
            'timeout': 30
        },
        {
            'nome': 'Teste 3: Primeiros 100 produtos ordenados por valor',
            'url': f"{base_url}/estoque_atual/?limite=100&ordem=valor_atual&reverso=true",
            'timeout': 45
        },
        {
            'nome': 'Teste 4: Estoque em data específica (limite 25)',
            'url': f"{base_url}/estoque_atual/?data=2025-01-15&limite=25",
            'timeout': 20
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
                
                # Informações básicas
                total_produtos = len(data.get('estoque', []))
                parametros = data.get('parametros', {})
                estatisticas = data.get('estatisticas', {})
                
                print(f"✅ Sucesso! {total_produtos} produto(s) retornados")
                
                # Mostra parâmetros
                print(f"📅 Data consulta: {parametros.get('data_consulta', 'N/A')}")
                if parametros.get('produto_id'):
                    print(f"🏷️  Produto ID: {parametros['produto_id']}")
                if parametros.get('limite_aplicado'):
                    print(f"📊 Limite aplicado: {parametros['limite_aplicado']}")
                
                # Mostra estatísticas se disponíveis
                if estatisticas:
                    print(f"📈 Produtos com estoque: {estatisticas.get('produtos_com_estoque', 0)}")
                    print(f"💰 Valor total atual: R$ {estatisticas.get('valor_total_atual', 0):,.2f}")
                
                # Mostra amostra dos dados
                if data.get('estoque'):
                    print("\n📦 Amostra dos produtos:")
                    for j, produto in enumerate(data['estoque'][:3]):  # Primeiros 3
                        print(f"   {j+1}. {produto.get('nome', 'N/A')} - Qty: {produto.get('quantidade_atual', 0)} - Valor: R$ {produto.get('valor_atual', 0):.2f}")
                    
                    if len(data['estoque']) > 3:
                        print(f"   ... e mais {len(data['estoque']) - 3} produtos")
                
                resultados.append({
                    'teste': teste['nome'],
                    'status': 'SUCESSO',
                    'tempo': tempo_resposta,
                    'produtos': total_produtos
                })
                
            elif response.status_code == 404:
                print(f"❌ Produto não encontrado")
                try:
                    error_data = response.json()
                    print(f"💬 Erro: {error_data.get('error', 'N/A')}")
                except:
                    pass
                
                resultados.append({
                    'teste': teste['nome'],
                    'status': 'PRODUTO_NAO_ENCONTRADO',
                    'tempo': tempo_resposta,
                    'produtos': 0
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
                    'produtos': 0
                })
                
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout após {teste['timeout']}s")
            resultados.append({
                'teste': teste['nome'],
                'status': 'TIMEOUT',
                'tempo': teste['timeout'],
                'produtos': 0
            })
            
        except requests.exceptions.ConnectionError:
            print(f"🔌 Erro de conexão - servidor não está rodando?")
            resultados.append({
                'teste': teste['nome'],
                'status': 'CONEXAO_ERRO',
                'tempo': 0,
                'produtos': 0
            })
            
        except Exception as e:
            print(f"💥 Erro inesperado: {str(e)}")
            resultados.append({
                'teste': teste['nome'],
                'status': 'ERRO_INESPERADO',
                'tempo': 0,
                'produtos': 0
            })
    
    # Resumo final
    print("\n" + "="*80)
    print("RESUMO DOS TESTES")
    print("="*80)
    
    sucessos = len([r for r in resultados if r['status'] == 'SUCESSO'])
    total_testes = len(resultados)
    
    print(f"📊 Testes executados: {total_testes}")
    print(f"✅ Sucessos: {sucessos}")
    print(f"❌ Falhas: {total_testes - sucessos}")
    print(f"📈 Taxa de sucesso: {(sucessos/total_testes)*100:.1f}%")
    
    print(f"\n📋 Detalhes por teste:")
    for resultado in resultados:
        status_icon = "✅" if resultado['status'] == 'SUCESSO' else "❌"
        print(f"{status_icon} {resultado['teste']}: {resultado['status']} ({resultado['tempo']:.2f}s, {resultado['produtos']} produtos)")
    
    if sucessos == total_testes:
        print(f"\n🎉 TODOS OS TESTES PASSARAM! O endpoint está funcionando corretamente.")
    else:
        print(f"\n⚠️  Alguns testes falharam. Verifique os detalhes acima.")
    
    print("="*80)

if __name__ == "__main__":
    testar_endpoint_corrigido()
