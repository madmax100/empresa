#!/usr/bin/env python
"""
Script para investigar a estrutura dos dados
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import Fornecedores
from contas.models.fluxo_caixa import FluxoCaixaLancamento
from datetime import datetime, date, timedelta
from django.db.models import Q, Sum, Count, Min, Max

def investigar_dados():
    """Investiga a estrutura dos dados"""
    
    print("🔍 INVESTIGAÇÃO DA ESTRUTURA DOS DADOS")
    print("="*50)
    
    # 1. Verificar FluxoCaixaLancamento geral
    total_lancamentos = FluxoCaixaLancamento.objects.count()
    print(f"📊 Total de lançamentos na base: {total_lancamentos}")
    
    if total_lancamentos > 0:
        # Verificar período dos dados
        periodo = FluxoCaixaLancamento.objects.aggregate(
            data_min=Min('data_realizacao'),
            data_max=Max('data_realizacao')
        )
        print(f"📅 Período dos dados: {periodo['data_min']} até {periodo['data_max']}")
        
        # Verificar status realizado
        status_dist = FluxoCaixaLancamento.objects.values('realizado').annotate(
            quantidade=Count('id')
        )
        print(f"📋 Distribuição por status realizado:")
        for item in status_dist:
            status = "Realizado" if item['realizado'] else "Não Realizado"
            qtd = item['quantidade']
            print(f"  - {status}: {qtd} lançamentos")
        
        # Verificar tipos
        tipos_dist = FluxoCaixaLancamento.objects.values('tipo').annotate(
            quantidade=Count('id')
        )
        print(f"📋 Distribuição por tipo:")
        for item in tipos_dist:
            tipo = item['tipo'] or 'SEM TIPO'
            qtd = item['quantidade']
            print(f"  - {tipo}: {qtd} lançamentos")
        
        # Verificar lançamentos com fornecedor
        com_fornecedor = FluxoCaixaLancamento.objects.filter(fornecedor__isnull=False).count()
        sem_fornecedor = FluxoCaixaLancamento.objects.filter(fornecedor__isnull=True).count()
        print(f"🏢 Lançamentos com fornecedor: {com_fornecedor}")
        print(f"🏢 Lançamentos sem fornecedor: {sem_fornecedor}")
        
        if com_fornecedor > 0:
            # Verificar alguns lançamentos com fornecedor
            lancamentos_exemplo = FluxoCaixaLancamento.objects.filter(
                fornecedor__isnull=False
            ).select_related('fornecedor')[:5]
            
            print(f"\n💼 EXEMPLOS DE LANÇAMENTOS COM FORNECEDOR:")
            for i, lanc in enumerate(lancamentos_exemplo, 1):
                data = lanc.data_realizacao.strftime('%Y-%m-%d') if lanc.data_realizacao else 'N/A'
                valor = lanc.valor
                fornecedor = lanc.fornecedor.nome if lanc.fornecedor else 'N/A'
                tipo_fornecedor = lanc.fornecedor.tipo if lanc.fornecedor and lanc.fornecedor.tipo else 'SEM TIPO'
                realizado = "Sim" if lanc.realizado else "Não"
                print(f"  {i}. {data} - R$ {valor:,.2f} - {fornecedor} ({tipo_fornecedor}) - Realizado: {realizado}")
        
        # Testar filtro sem restrição de período
        print(f"\n🔍 TESTANDO FILTRO POR TIPO DE FORNECEDOR (SEM RESTRIÇÃO DE PERÍODO):")
        
        fornecedores_fixos = Fornecedores.objects.filter(
            Q(tipo__icontains='DESPESA FIXA') | Q(tipo__icontains='CUSTO FIXO')
        ).values_list('id', flat=True)
        
        lancamentos_filtrados = FluxoCaixaLancamento.objects.filter(
            fornecedor_id__in=fornecedores_fixos,
            tipo='saida'
        )
        
        total_filtrados = lancamentos_filtrados.count()
        realizados_filtrados = lancamentos_filtrados.filter(realizado=True).count()
        
        print(f"  - Total de lançamentos de fornecedores fixos: {total_filtrados}")
        print(f"  - Lançamentos realizados: {realizados_filtrados}")
        print(f"  - Lançamentos não realizados: {total_filtrados - realizados_filtrados}")
        
        if total_filtrados > 0:
            # Mostrar alguns exemplos
            exemplos = lancamentos_filtrados.select_related('fornecedor')[:5]
            print(f"\n📋 EXEMPLOS DE LANÇAMENTOS DE FORNECEDORES FIXOS:")
            for i, lanc in enumerate(exemplos, 1):
                data = lanc.data_realizacao.strftime('%Y-%m-%d') if lanc.data_realizacao else 'N/A'
                valor = lanc.valor
                fornecedor = lanc.fornecedor.nome if lanc.fornecedor else 'N/A'
                tipo_fornecedor = lanc.fornecedor.tipo if lanc.fornecedor and lanc.fornecedor.tipo else 'SEM TIPO'
                realizado = "Sim" if lanc.realizado else "Não"
                print(f"  {i}. {data} - R$ {valor:,.2f} - {fornecedor} ({tipo_fornecedor}) - Realizado: {realizado}")
    
    print("\n" + "="*50)
    print("✅ INVESTIGAÇÃO CONCLUÍDA!")

if __name__ == "__main__":
    investigar_dados()
