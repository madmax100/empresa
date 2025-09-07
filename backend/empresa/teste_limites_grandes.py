#!/usr/bin/env python
"""
Teste de limites maiores para verificar se o erro JSON foi corrigido
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

def testar_limites_grandes():
    """Testa o endpoint com limites maiores para verificar correção do JSON"""
    
    print("="*80)
    print("TESTE DE LIMITES GRANDES - VERIFICAÇÃO SERIALIZAÇÃO JSON")
    print("="*80)
    
    base_url = "http://127.0.0.1:8000/api/estoque-controle"
    
    testes = [
        {
            'nome': 'Teste 1: 200 produtos',
            'url': f"{base_url}/estoque_atual/?limite=200",
            'timeout': 60
        },
        {
            'nome': 'Teste 2: 300 produtos',
            'url': f"{base_url}/estoque_atual/?limite=300",
            'timeout': 90
        },
        {
            'nome': 'Teste 3: 400 produtos',
            'url': f"{base_url}/estoque_atual/?limite=400",
            'timeout': 120
        },
        {
            'nome': 'Teste 4: 500 produtos (limite que estava falhando)',
            'url': f"{base_url}/estoque_atual/?limite=500",
            'timeout': 150
        }
    ]
    
    resultados = []
    
    for teste in testes:
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
                try:
                    data = response.json()
                    
                    # Verifica a estrutura dos dados
                    estoque = data.get('estoque', [])
                    estatisticas = data.get('estatisticas', {})
                    parametros = data.get('parametros', {})
                    
                    print(f"✅ Sucesso! {len(estoque)} produto(s) retornados")
                    print(f"💰 Valor total: R$ {estatisticas.get('valor_total_atual', 0):,.2f}")
                    print(f"📈 Produtos com estoque: {estatisticas.get('produtos_com_estoque', 0)}")
                    
                    # Verifica se as movimentações recentes estão sendo serializadas corretamente
                    produtos_com_movs = 0
                    for produto in estoque[:5]:  # Verifica primeiros 5
                        movs_recentes = produto.get('movimentacoes_recentes', [])
                        if movs_recentes:
                            produtos_com_movs += 1
                            # Verifica se a primeira movimentação tem estrutura JSON válida
                            primeira_mov = movs_recentes[0]
                            if isinstance(primeira_mov, dict) and 'data' in primeira_mov:
                                print(f"✅ Movimentações serializadas corretamente")
                                break
                    
                    print(f"📦 Produtos com movimentações recentes: {produtos_com_movs}/5 (amostra)")
                    
                    resultados.append({
                        'teste': teste['nome'],
                        'status': 'SUCESSO',
                        'tempo': tempo_resposta,
                        'produtos': len(estoque),
                        'valor_total': estatisticas.get('valor_total_atual', 0)
                    })
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Erro ao decodificar JSON: {str(e)}")
                    resultados.append({
                        'teste': teste['nome'],
                        'status': 'ERRO_JSON',
                        'tempo': tempo_resposta,
                        'produtos': 0,
                        'valor_total': 0
                    })
                
            else:
                print(f"❌ Erro HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"💬 Erro: {error_data.get('error', 'N/A')}")
                except:
                    print(f"💬 Resposta: {response.text[:300]}...")
                
                resultados.append({
                    'teste': teste['nome'],
                    'status': 'ERRO_HTTP',
                    'tempo': tempo_resposta,
                    'produtos': 0,
                    'valor_total': 0
                })
                
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout após {teste['timeout']}s")
            resultados.append({
                'teste': teste['nome'],
                'status': 'TIMEOUT',
                'tempo': teste['timeout'],
                'produtos': 0,
                'valor_total': 0
            })
            
        except Exception as e:
            print(f"💥 Erro inesperado: {str(e)}")
            resultados.append({
                'teste': teste['nome'],
                'status': 'ERRO_INESPERADO',
                'tempo': 0,
                'produtos': 0,
                'valor_total': 0
            })
    
    # Resumo final
    print("\n" + "="*80)
    print("RESUMO DOS TESTES - LIMITES GRANDES")
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
        print(f"{status_icon} {resultado['teste']}: {resultado['status']} ({resultado['tempo']:.1f}s, {resultado['produtos']} produtos, R$ {resultado['valor_total']:,.2f})")
    
    if sucessos == total_testes:
        print(f"\n🎉 TODOS OS TESTES PASSARAM! O problema de serialização JSON foi corrigido!")
        print(f"✅ O endpoint agora suporta limites grandes sem erro de serialização")
    else:
        print(f"\n⚠️  Alguns testes falharam. Verifique os detalhes acima.")
    
    print("="*80)

if __name__ == "__main__":
    testar_limites_grandes()
