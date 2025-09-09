#!/usr/bin/env python
"""
Script para verificar dados de fornecedores com tipos fixos
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
from django.db.models import Q, Sum, Count

def verificar_fornecedores_tipos_fixos():
    """Verifica fornecedores com tipos fixos e seus dados"""
    
    print("🔍 ANÁLISE DE FORNECEDORES COM TIPOS FIXOS")
    print("="*50)
    
    # Buscar fornecedores com tipos fixos
    fornecedores_fixos = Fornecedores.objects.filter(
        Q(tipo__icontains='DESPESA FIXA') | Q(tipo__icontains='CUSTO FIXO')
    )
    
    print(f"📊 Total de fornecedores com tipos fixos: {fornecedores_fixos.count()}")
    
    # Mostrar distribuição por tipo
    tipos_distribuicao = fornecedores_fixos.values('tipo').annotate(
        quantidade=Count('id')
    ).order_by('-quantidade')
    
    print("\n📋 Distribuição por tipo:")
    for item in tipos_distribuicao:
        tipo = item['tipo'] or 'SEM TIPO'
        qtd = item['quantidade']
        print(f"  - {tipo}: {qtd} fornecedores")
    
    # Verificar se há lançamentos para esses fornecedores (período maior)
    data_fim = date.today()
    data_inicio = data_fim - timedelta(days=365)  # Último ano
    
    print(f"\n💰 VERIFICANDO LANÇAMENTOS NO ÚLTIMO ANO ({data_inicio} até {data_fim}):")
    
    lancamentos = FluxoCaixaLancamento.objects.filter(
        fornecedor_id__in=fornecedores_fixos.values_list('id', flat=True),
        realizado=True,
        tipo='saida',
        data_realizacao__date__range=(data_inicio, data_fim)
    )
    
    total_lancamentos = lancamentos.count()
    total_valor = lancamentos.aggregate(total=Sum('valor'))['total'] or 0
    
    print(f"  - Total de lançamentos: {total_lancamentos}")
    print(f"  - Valor total pago: R$ {total_valor:,.2f}")
    
    if total_lancamentos > 0:
        # Top fornecedores com pagamentos
        top_fornecedores = lancamentos.values(
            'fornecedor__nome', 'fornecedor__tipo'
        ).annotate(
            total_pago=Sum('valor'),
            qtd_lancamentos=Count('id')
        ).order_by('-total_pago')[:10]
        
        print(f"\n🏆 TOP 10 FORNECEDORES COM PAGAMENTOS:")
        for i, item in enumerate(top_fornecedores, 1):
            nome = item['fornecedor__nome']
            tipo = item['fornecedor__tipo']
            total = item['total_pago']
            qtd = item['qtd_lancamentos']
            print(f"  {i}. {nome} ({tipo}): R$ {total:,.2f} ({qtd} lançamentos)")
        
        # Últimos lançamentos
        ultimos_lancamentos = lancamentos.select_related('fornecedor').order_by('-data_realizacao')[:5]
        
        print(f"\n🕐 ÚLTIMOS 5 LANÇAMENTOS:")
        for i, lanc in enumerate(ultimos_lancamentos, 1):
            data = lanc.data_realizacao.strftime('%Y-%m-%d')
            valor = lanc.valor
            fornecedor = lanc.fornecedor.nome if lanc.fornecedor else 'N/A'
            tipo = lanc.fornecedor.tipo if lanc.fornecedor and lanc.fornecedor.tipo else 'N/A'
            descricao = lanc.descricao[:50] if lanc.descricao else 'N/A'
            print(f"  {i}. {data} - R$ {valor:,.2f} - {fornecedor} ({tipo})")
            print(f"     {descricao}...")
    
    print("\n" + "="*50)
    print("✅ ANÁLISE CONCLUÍDA!")

if __name__ == "__main__":
    verificar_fornecedores_tipos_fixos()
