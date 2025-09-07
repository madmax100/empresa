#!/usr/bin/env python
"""
Teste direto para verificar variação de estoque por data usando produto conhecido
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

def testar_variacao_direta():
    """Testa variação de estoque usando produto conhecido"""
    
    print("="*80)
    print("TESTE DIRETO DE VARIAÇÃO DE ESTOQUE POR DATA")
    print("="*80)
    
    base_url = "http://127.0.0.1:8000/api/estoque-controle"
    
    # Vamos usar um produto que tem movimentações após o estoque inicial (ID 3391)
    produto_id = 3391
    produto_nome = "Produto com movimentações posteriores"
    
    print(f"🔍 Testando produto: {produto_nome} (ID: {produto_id})")
    print()
    
    # Datas para teste
    datas_teste = [
        '2025-01-01',  # Data inicial do estoque
        '2025-01-15',  # 15 dias após início
        '2025-03-01',  # 2 meses após início
        '2025-06-01',  # 5 meses após início
        '2025-09-06'   # Data atual
    ]
    
    print("📅 Testando estoque nas seguintes datas:")
    for data in datas_teste:
        print(f"   • {data}")
    print()
    
    resultados = []
    
    for data_teste in datas_teste:
        print(f"📅 Testando data: {data_teste}")
        
        try:
            url = f"{base_url}/estoque_atual/?produto_id={produto_id}&data={data_teste}"
            inicio = datetime.now()
            response = requests.get(url, timeout=15)
            tempo = (datetime.now() - inicio).total_seconds()
            
            print(f"   ⏱️  Tempo: {tempo:.2f}s")
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data_response = response.json()
                estoque = data_response.get('estoque', [])
                parametros = data_response.get('parametros', {})
                
                if estoque:
                    produto = estoque[0]
                    quantidade_inicial = produto.get('quantidade_inicial', 0)
                    quantidade_atual = produto.get('quantidade_atual', 0)
                    valor_inicial = produto.get('valor_inicial', 0)
                    valor_atual = produto.get('valor_atual', 0)
                    variacao_qty = produto.get('variacao_quantidade', 0)
                    variacao_valor = produto.get('variacao_valor', 0)
                    total_movs = produto.get('total_movimentacoes', 0)
                    movs_recentes = produto.get('movimentacoes_recentes', [])
                    
                    print(f"   📦 Quantidade inicial: {quantidade_inicial}")
                    print(f"   📦 Quantidade atual: {quantidade_atual}")
                    print(f"   📈 Variação quantidade: {variacao_qty:+.1f}")
                    print(f"   💰 Valor inicial: R$ {valor_inicial:,.2f}")
                    print(f"   💰 Valor atual: R$ {valor_atual:,.2f}")
                    print(f"   💰 Variação valor: R$ {variacao_valor:+,.2f}")
                    print(f"   🔄 Total movimentações até {data_teste}: {total_movs}")
                    print(f"   📋 Movimentações recentes: {len(movs_recentes)}")
                    
                    resultados.append({
                        'data': data_teste,
                        'quantidade_inicial': float(quantidade_inicial),
                        'quantidade_atual': float(quantidade_atual),
                        'valor_inicial': float(valor_inicial),
                        'valor_atual': float(valor_atual),
                        'variacao_qty': float(variacao_qty),
                        'variacao_valor': float(variacao_valor),
                        'total_movimentacoes': int(total_movs),
                        'tempo_resposta': tempo,
                        'status': 'sucesso'
                    })
                    
                    print("   ✅ Dados obtidos com sucesso")
                else:
                    print("   ❌ Produto não encontrado no estoque")
                    resultados.append({
                        'data': data_teste,
                        'status': 'produto_nao_encontrado',
                        'tempo_resposta': tempo
                    })
            else:
                print(f"   ❌ Erro HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   💬 Erro: {error_data.get('error', 'N/A')}")
                except:
                    pass
                
                resultados.append({
                    'data': data_teste,
                    'status': 'erro_http',
                    'tempo_resposta': tempo
                })
                
        except Exception as e:
            print(f"   ❌ Erro inesperado: {str(e)}")
            resultados.append({
                'data': data_teste,
                'status': 'erro',
                'tempo_resposta': 0
            })
        
        print()
    
    # Análise dos resultados
    print("="*80)
    print("ANÁLISE DOS RESULTADOS")
    print("="*80)
    
    resultados_validos = [r for r in resultados if r.get('status') == 'sucesso']
    
    if len(resultados_validos) >= 2:
        print("📊 TABELA COMPARATIVA:")
        print()
        print(f"{'Data':<12} {'Qty Atual':<10} {'Valor Atual':<15} {'Movs':<6} {'Var Qty':<10} {'Var Valor':<12}")
        print("-" * 80)
        
        for resultado in resultados_validos:
            data = resultado['data']
            qty = resultado['quantidade_atual']
            valor = resultado['valor_atual']
            movs = resultado['total_movimentacoes']
            var_qty = resultado['variacao_qty']
            var_valor = resultado['variacao_valor']
            
            print(f"{data:<12} {qty:<10.1f} R$ {valor:<12,.2f} {movs:<6} {var_qty:<+10.1f} R$ {var_valor:<+10,.2f}")
        
        print()
        
        # Análise de variações
        quantidades = [r['quantidade_atual'] for r in resultados_validos]
        valores = [r['valor_atual'] for r in resultados_validos]
        movimentacoes = [r['total_movimentacoes'] for r in resultados_validos]
        
        qty_min, qty_max = min(quantidades), max(quantidades)
        valor_min, valor_max = min(valores), max(valores)
        movs_min, movs_max = min(movimentacoes), max(movimentacoes)
        
        print("📈 ANÁLISE DE VARIAÇÕES:")
        print()
        
        if qty_max != qty_min:
            print(f"✅ QUANTIDADE VARIA CORRETAMENTE")
            print(f"   📊 Mínima: {qty_min:.1f}")
            print(f"   📊 Máxima: {qty_max:.1f}")
            print(f"   📊 Amplitude: {qty_max - qty_min:.1f}")
        else:
            print(f"⚠️  QUANTIDADE NÃO VARIA")
            print(f"   📊 Valor constante: {qty_min:.1f}")
            print(f"   💡 Possível motivo: produto sem movimentações")
        
        print()
        
        if valor_max != valor_min:
            print(f"✅ VALOR VARIA CORRETAMENTE")
            print(f"   💰 Mínimo: R$ {valor_min:,.2f}")
            print(f"   💰 Máximo: R$ {valor_max:,.2f}")
            print(f"   💰 Amplitude: R$ {valor_max - valor_min:,.2f}")
        else:
            print(f"⚠️  VALOR NÃO VARIA")
            print(f"   💰 Valor constante: R$ {valor_min:,.2f}")
        
        print()
        
        if movs_max != movs_min:
            print(f"✅ MOVIMENTAÇÕES ACUMULAM CORRETAMENTE")
            print(f"   🔄 Mínimo: {movs_min}")
            print(f"   🔄 Máximo: {movs_max}")
            print(f"   🔄 Crescimento: {movs_max - movs_min} movimentações")
        else:
            print(f"⚠️  MOVIMENTAÇÕES NÃO VARIAM")
            print(f"   🔄 Valor constante: {movs_min}")
        
        # Verificação temporal
        print("\n🕐 VERIFICAÇÃO TEMPORAL:")
        if resultados_validos[0]['total_movimentacoes'] <= resultados_validos[-1]['total_movimentacoes']:
            print("✅ Ordem temporal correta: movimentações crescem com o tempo")
        else:
            print("❌ Ordem temporal incorreta: movimentações deveriam crescer com o tempo")
        
        # Performance
        tempos = [r['tempo_resposta'] for r in resultados_validos]
        tempo_medio = sum(tempos) / len(tempos)
        print(f"\n⚡ PERFORMANCE:")
        print(f"   ⏱️  Tempo médio: {tempo_medio:.2f}s")
        print(f"   ⏱️  Tempo máximo: {max(tempos):.2f}s")
        print(f"   ⏱️  Tempo mínimo: {min(tempos):.2f}s")
        
    else:
        print("❌ DADOS INSUFICIENTES PARA ANÁLISE")
        print(f"   Apenas {len(resultados_validos)} de {len(resultados)} testes foram bem-sucedidos")
        
        print("\n📋 Status dos testes:")
        for resultado in resultados:
            data = resultado['data']
            status = resultado['status']
            tempo = resultado.get('tempo_resposta', 0)
            print(f"   {data}: {status} ({tempo:.2f}s)")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    testar_variacao_direta()
