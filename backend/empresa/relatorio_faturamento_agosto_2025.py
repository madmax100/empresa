#!/usr/bin/env python3
"""
Relatório de Faturamento - Agosto/2025
Análise dos contratos vigentes e seus valores mensais
"""

import os
import sys
import django
import requests
from datetime import datetime
import json

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

def relatorio_faturamento_agosto_2025():
    """
    Gera relatório detalhado do faturamento em agosto/2025
    """
    print("=" * 80)
    print("📊 RELATÓRIO DE FATURAMENTO - AGOSTO/2025")
    print("=" * 80)
    
    # Período específico solicitado
    data_inicial = "2025-08-01"
    data_final = "2025-08-31"
    
    print(f"\n📅 Período analisado: {data_inicial} a {data_final}")
    
    # Consultar endpoint
    url = "http://localhost:8000/api/contratos_locacao/suprimentos/"
    params = {
        'data_inicial': data_inicial,
        'data_final': data_final
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Resumo financeiro geral
            resumo_financeiro = data.get('resumo_financeiro', {})
            print(f"\n💰 RESUMO FINANCEIRO GERAL:")
            print(f"   Faturamento Total: R$ {resumo_financeiro.get('faturamento_total_periodo', 0):,.2f}")
            print(f"   Custo Suprimentos: R$ {resumo_financeiro.get('custo_total_suprimentos', 0):,.2f}")
            print(f"   Margem Bruta: R$ {resumo_financeiro.get('margem_bruta_total', 0):,.2f}")
            print(f"   % Margem: {resumo_financeiro.get('percentual_margem_total', 0):.1f}%")
            
            # Resumo geral
            resumo = data.get('resumo', {})
            print(f"\n📋 RESUMO GERAL:")
            print(f"   Contratos vigentes: {resumo.get('total_contratos_vigentes', 0)}")
            print(f"   Contratos com atividade: {resumo.get('contratos_com_atividade', 0)}")
            print(f"   Total de notas: {resumo.get('total_notas', 0)}")
            
            # Análise detalhada por contrato
            resultados = data.get('resultados', [])
            
            print(f"\n📊 CONTRATOS VIGENTES E VALORES MENSAIS:")
            print("=" * 80)
            
            # Ordenar por valor mensal (decrescente)
            contratos_com_valor = []
            contratos_sem_valor = []
            
            for resultado in resultados:
                valores = resultado.get('valores_contratuais', {})
                valor_mensal = valores.get('valor_mensal', 0)
                
                if valor_mensal > 0:
                    contratos_com_valor.append(resultado)
                else:
                    contratos_sem_valor.append(resultado)
            
            # Ordenar por valor mensal decrescente
            contratos_com_valor.sort(key=lambda x: x['valores_contratuais']['valor_mensal'], reverse=True)
            
            print(f"\n🏆 TOP CONTRATOS POR VALOR MENSAL ({len(contratos_com_valor)} contratos):")
            print("-" * 80)
            
            total_faturamento_calculado = 0
            
            for i, contrato in enumerate(contratos_com_valor, 1):
                contrato_id = contrato.get('contrato_id')
                contrato_numero = contrato.get('contrato_numero', 'N/A')
                cliente = contrato.get('cliente', {})
                valores = contrato.get('valores_contratuais', {})
                analise = contrato.get('analise_financeira', {})
                vigencia = contrato.get('vigencia', {})
                
                valor_mensal = valores.get('valor_mensal', 0)
                faturamento_periodo = valores.get('faturamento_periodo', 0)
                custo_suprimentos = analise.get('custo_suprimentos', 0)
                margem_bruta = analise.get('margem_bruta', 0)
                percentual_margem = analise.get('percentual_margem', 0)
                meses_periodo = vigencia.get('meses_no_periodo', 0)
                
                total_faturamento_calculado += faturamento_periodo
                
                print(f"\n{i:2d}. Contrato {contrato_id} ({contrato_numero})")
                print(f"    Cliente: {cliente.get('nome', 'N/A')}")
                print(f"    💰 Valor Mensal: R$ {valor_mensal:,.2f}")
                print(f"    📅 Meses no período: {meses_periodo}")
                print(f"    💵 Faturamento período: R$ {faturamento_periodo:,.2f}")
                print(f"    💸 Custo suprimentos: R$ {custo_suprimentos:,.2f}")
                print(f"    📈 Margem: R$ {margem_bruta:,.2f} ({percentual_margem:.1f}%)")
                print(f"    🗓️  Vigência: {vigencia.get('inicio')} até {vigencia.get('fim') or 'ativo'}")
            
            # Contratos sem valor definido
            if contratos_sem_valor:
                print(f"\n⚠️  CONTRATOS SEM VALOR MENSAL DEFINIDO ({len(contratos_sem_valor)} contratos):")
                print("-" * 60)
                for contrato in contratos_sem_valor:
                    contrato_id = contrato.get('contrato_id')
                    cliente = contrato.get('cliente', {})
                    print(f"   • Contrato {contrato_id} - {cliente.get('nome', 'N/A')}")
            
            # Estatísticas finais
            print(f"\n📈 ESTATÍSTICAS FINAIS:")
            print("=" * 50)
            print(f"   Total de contratos analisados: {len(resultados)}")
            print(f"   Contratos com valor mensal: {len(contratos_com_valor)}")
            print(f"   Contratos sem valor mensal: {len(contratos_sem_valor)}")
            print(f"   Faturamento total calculado: R$ {total_faturamento_calculado:,.2f}")
            
            if len(contratos_com_valor) > 0:
                media_valor_mensal = sum([c['valores_contratuais']['valor_mensal'] for c in contratos_com_valor]) / len(contratos_com_valor)
                print(f"   Valor mensal médio: R$ {media_valor_mensal:,.2f}")
            
            # Verificar consistência
            faturamento_api = resumo_financeiro.get('faturamento_total_periodo', 0)
            diferenca = abs(total_faturamento_calculado - faturamento_api)
            
            print(f"\n🔍 VERIFICAÇÃO DE CONSISTÊNCIA:")
            print(f"   Faturamento pela API: R$ {faturamento_api:,.2f}")
            print(f"   Faturamento calculado: R$ {total_faturamento_calculado:,.2f}")
            print(f"   Diferença: R$ {diferenca:,.2f}")
            
            if diferenca < 0.01:
                print("   ✅ Cálculos consistentes!")
            else:
                print("   ⚠️  Pequena diferença detectada")
                
        else:
            print(f"❌ Erro na requisição: Status {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Servidor não está rodando")
        print("💡 Execute: python manage.py runserver")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
    
    print(f"\n" + "=" * 80)

if __name__ == "__main__":
    relatorio_faturamento_agosto_2025()
