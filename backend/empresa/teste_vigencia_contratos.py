#!/usr/bin/env python3
"""
Teste para verificar se o endpoint suprimentos-por-contrato
está corretamente filtrando por vigência dos contratos
"""

import os
import sys
import django
import requests
from datetime import datetime, timedelta

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import ContratosLocacao
from django.contrib.auth.models import User

def teste_vigencia_contratos():
    """
    Testa se o endpoint considera a vigência dos contratos
    """
    print("=" * 80)
    print("TESTE DE VIGÊNCIA - ENDPOINT SUPRIMENTOS POR CONTRATO")
    print("=" * 80)
    
    # Definir período de teste
    hoje = datetime.now().date()
    data_inicial = hoje - timedelta(days=30)
    data_final = hoje + timedelta(days=30)
    
    print(f"\n📅 Período de teste:")
    print(f"   Data inicial: {data_inicial}")
    print(f"   Data final: {data_final}")
    
    # Analisar contratos no banco
    print(f"\n📋 Análise de contratos:")
    
    # Contratos que terminaram antes do período
    contratos_expirados = ContratosLocacao.objects.filter(
        fim__lt=data_inicial
    ).count()
    
    # Contratos que começam depois do período
    contratos_futuros = ContratosLocacao.objects.filter(
        inicio__gt=data_final
    ).count()
    
    # Contratos vigentes no período
    from django.db.models import Q
    contratos_vigentes = ContratosLocacao.objects.filter(
        Q(inicio__lte=data_final) &
        (Q(fim__gte=data_inicial) | Q(fim__isnull=True))
    ).count()
    
    total_contratos = ContratosLocacao.objects.count()
    
    print(f"   Total de contratos: {total_contratos}")
    print(f"   Contratos vigentes no período: {contratos_vigentes}")
    print(f"   Contratos expirados antes do período: {contratos_expirados}")
    print(f"   Contratos que iniciam após o período: {contratos_futuros}")
    
    # Teste do endpoint
    url = "http://localhost:8000/api/contratos_locacao/suprimentos/"
    params = {
        'data_inicial': data_inicial.strftime('%Y-%m-%d'),
        'data_final': data_final.strftime('%Y-%m-%d')
    }
    
    print(f"\n🔗 Testando endpoint:")
    print(f"   URL: {url}")
    print(f"   Parâmetros: {params}")
    
    try:
        response = requests.get(url, params=params)
        
        print(f"\n📊 Resultado do teste:")
        print(f"   Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verificar se o filtro de vigência foi aplicado
            filtros = data.get('filtros_aplicados', {})
            vigencia_considerada = filtros.get('vigencia_considerada', False)
            
            print(f"   Vigência considerada: {vigencia_considerada}")
            
            resumo = data.get('resumo', {})
            contratos_retornados = resumo.get('total_contratos_vigentes', 0)
            contratos_com_atividade = resumo.get('contratos_com_atividade', 0)
            
            print(f"   Contratos vigentes retornados: {contratos_retornados}")
            print(f"   Contratos com atividade: {contratos_com_atividade}")
            
            # Verificar se o número de contratos bate
            if contratos_retornados == contratos_vigentes:
                print("   ✅ TESTE PASSOU - Número de contratos correto")
            else:
                print("   ❌ TESTE FALHOU - Número de contratos divergente")
                print(f"      Esperado: {contratos_vigentes}")
                print(f"      Retornado: {contratos_retornados}")
            
            # Verificar alguns contratos específicos
            resultados = data.get('resultados', [])
            print(f"\n🔍 Verificação de vigência dos contratos retornados:")
            
            for resultado in resultados[:5]:  # Primeiros 5 contratos
                contrato_id = resultado.get('contrato_id')
                vigencia = resultado.get('vigencia', {})
                inicio = vigencia.get('inicio')
                fim = vigencia.get('fim')
                ativo = vigencia.get('ativo_no_periodo')
                
                print(f"   Contrato {contrato_id}: {inicio} até {fim or 'ativo'} - Ativo: {ativo}")
        
        else:
            print(f"   ❌ Erro na requisição: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Erro: Servidor não está rodando")
        print("   💡 Execute: python manage.py runserver")
    except Exception as e:
        print(f"   ❌ Erro inesperado: {e}")
    
    print(f"\n" + "=" * 80)

if __name__ == "__main__":
    teste_vigencia_contratos()
