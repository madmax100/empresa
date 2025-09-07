#!/usr/bin/env python
"""
Script para consultar estoque atual
Mostra saldos atuais, movimentações recentes e alertas de estoque
"""

import os
import sys
import django
from datetime import datetime, date, timedelta
from decimal import Decimal
from django.db.models import Sum, Max, Count, Case, When, Value, DecimalField, Q, F
from django.db.models.functions import Coalesce

# Configurar Django
sys.path.append(os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models import (
    SaldosEstoque, 
    MovimentacoesEstoque, 
    Produtos,
    TiposMovimentacaoEstoque,
    LocaisEstoque
)

def consultar_estoque_geral():
    """Consulta resumo geral do estoque"""
    print("=" * 80)
    print("CONSULTA DE ESTOQUE ATUAL")
    print("=" * 80)
    
    # Total de produtos cadastrados
    total_produtos = Produtos.objects.count()
    print(f"Total de produtos cadastrados: {total_produtos}")
    
    # Total de produtos com estoque
    produtos_com_estoque = SaldosEstoque.objects.filter(quantidade__gt=0).count()
    print(f"Produtos com estoque positivo: {produtos_com_estoque}")
    
    # Valor total do estoque
    from django.db.models import F
    valor_estoque = SaldosEstoque.objects.aggregate(
        valor_total=Sum(
            Case(
                When(custo_medio__isnull=False, then=F('quantidade') * F('custo_medio')),
                default=Value(0),
                output_field=DecimalField(max_digits=15, decimal_places=2)
            )
        )
    )['valor_total'] or Decimal('0')
    
    print(f"Valor total estimado do estoque: R$ {valor_estoque:,.2f}")
    
    # Última atualização
    ultima_movimentacao = MovimentacoesEstoque.objects.aggregate(
        ultima=Max('data_movimentacao')
    )['ultima']
    
    if ultima_movimentacao:
        print(f"Última movimentação: {ultima_movimentacao.strftime('%d/%m/%Y %H:%M')}")
    
    print()

def consultar_saldos_detalhados(limite=20):
    """Consulta saldos detalhados por produto"""
    print("SALDOS DETALHADOS POR PRODUTO")
    print("-" * 80)
    print(f"{'Código':<15} {'Nome':<30} {'Local':<15} {'Qtd':<10} {'Custo Médio':<12} {'Valor Total':<15}")
    print("-" * 80)
    
    saldos = SaldosEstoque.objects.select_related(
        'produto_id', 'local_id'
    ).filter(
        quantidade__gt=0
    ).order_by('-quantidade')[:limite]
    
    total_valor = Decimal('0')
    
    for saldo in saldos:
        produto = saldo.produto_id
        local = saldo.local_id.descricao if saldo.local_id else 'N/D'
        quantidade = saldo.quantidade
        custo_medio = saldo.custo_medio or Decimal('0')
        valor_total = quantidade * custo_medio
        total_valor += valor_total
        
        print(f"{produto.codigo:<15} {produto.nome[:30]:<30} {local:<15} {quantidade:<10} R$ {custo_medio:<10.2f} R$ {valor_total:<13.2f}")
    
    print("-" * 80)
    print(f"{'TOTAL':<75} R$ {total_valor:<13.2f}")
    print()

def consultar_produtos_sem_estoque():
    """Lista produtos sem estoque ou com estoque zero"""
    print("PRODUTOS SEM ESTOQUE")
    print("-" * 60)
    
    # Produtos sem registro na tabela de saldos
    produtos_sem_saldo = Produtos.objects.filter(
        saldosestoque__isnull=True
    ).distinct()
    
    # Produtos com saldo zero
    produtos_saldo_zero = Produtos.objects.filter(
        saldosestoque__quantidade=0
    ).distinct()
    
    todos_sem_estoque = produtos_sem_saldo.union(produtos_saldo_zero)
    
    print(f"Total de produtos sem estoque: {todos_sem_estoque.count()}")
    
    print(f"{'Código':<15} {'Nome':<40}")
    print("-" * 60)
    
    for produto in todos_sem_estoque[:20]:  # Limita a 20 para não sobrecarregar
        print(f"{produto.codigo:<15} {produto.nome[:40]:<40}")
    
    if todos_sem_estoque.count() > 20:
        print(f"... e mais {todos_sem_estoque.count() - 20} produtos")
    
    print()

def consultar_movimentacoes_recentes(dias=7):
    """Consulta movimentações recentes"""
    print(f"MOVIMENTAÇÕES DOS ÚLTIMOS {dias} DIAS")
    print("-" * 80)
    
    data_limite = datetime.now() - timedelta(days=dias)
    
    movimentacoes = MovimentacoesEstoque.objects.filter(
        data_movimentacao__gte=data_limite
    ).select_related(
        'produto', 'tipo_movimentacao'
    ).order_by('-data_movimentacao')[:30]
    
    print(f"{'Data':<12} {'Tipo':<8} {'Produto':<20} {'Qtd':<10} {'Valor Unit.':<12} {'Valor Total':<15}")
    print("-" * 80)
    
    for mov in movimentacoes:
        data = mov.data_movimentacao.strftime('%d/%m/%Y')
        tipo = mov.tipo_movimentacao.codigo if mov.tipo_movimentacao else 'N/D'
        produto = mov.produto.codigo if mov.produto else 'N/D'
        quantidade = mov.quantidade
        custo_unit = mov.custo_unitario or Decimal('0')
        valor_total = mov.valor_total or (quantidade * custo_unit)
        
        print(f"{data:<12} {tipo:<8} {produto:<20} {quantidade:<10} R$ {custo_unit:<10.2f} R$ {valor_total:<13.2f}")
    
    print()

def consultar_alertas_estoque():
    """Gera alertas de estoque"""
    print("ALERTAS DE ESTOQUE")
    print("-" * 60)
    
    alertas = []
    
    # Produtos com estoque baixo (assumindo estoque mínimo = 5)
    produtos_estoque_baixo = SaldosEstoque.objects.filter(
        quantidade__lte=5,
        quantidade__gt=0
    ).select_related('produto_id')
    
    if produtos_estoque_baixo.exists():
        alertas.append(f"🔸 {produtos_estoque_baixo.count()} produtos com estoque baixo (≤5 unidades)")
    
    # Produtos sem movimentação há muito tempo
    data_limite = datetime.now() - timedelta(days=90)
    produtos_parados = SaldosEstoque.objects.filter(
        quantidade__gt=0,
        ultima_movimentacao__lt=data_limite
    ).select_related('produto_id')
    
    if produtos_parados.exists():
        alertas.append(f"⚠️  {produtos_parados.count()} produtos sem movimentação há mais de 90 dias")
    
    # Produtos sem custo médio
    produtos_sem_custo = SaldosEstoque.objects.filter(
        quantidade__gt=0,
        custo_medio__isnull=True
    )
    
    if produtos_sem_custo.exists():
        alertas.append(f"💰 {produtos_sem_custo.count()} produtos sem custo médio definido")
    
    if alertas:
        for alerta in alertas:
            print(alerta)
    else:
        print("✅ Nenhum alerta identificado")
    
    print()

def consultar_por_local():
    """Consulta estoque por local"""
    print("ESTOQUE POR LOCAL")
    print("-" * 60)
    
    locais = LocaisEstoque.objects.annotate(
        total_produtos=Count('saldosestoque'),
        quantidade_total=Sum('saldosestoque__quantidade'),
        valor_total=Sum(
            Case(
                When(saldosestoque__custo_medio__isnull=False, 
                     then=F('saldosestoque__quantidade') * F('saldosestoque__custo_medio')),
                default=Value(0),
                output_field=DecimalField(max_digits=15, decimal_places=2)
            )
        )
    ).filter(total_produtos__gt=0)
    
    print(f"{'Local':<25} {'Produtos':<10} {'Qtd Total':<12} {'Valor Total':<15}")
    print("-" * 60)
    
    for local in locais:
        nome = local.descricao[:25]
        produtos = local.total_produtos
        quantidade = local.quantidade_total or 0
        valor = local.valor_total or Decimal('0')
        
        print(f"{nome:<25} {produtos:<10} {quantidade:<12} R$ {valor:<13.2f}")
    
    print()

def main():
    """Função principal"""
    try:
        print(f"Executado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print()
        
        # Consultas principais
        consultar_estoque_geral()
        consultar_saldos_detalhados()
        consultar_produtos_sem_estoque()
        consultar_movimentacoes_recentes()
        consultar_alertas_estoque()
        consultar_por_local()
        
        print("=" * 80)
        print("CONSULTA FINALIZADA")
        print("=" * 80)
        
    except Exception as e:
        print(f"Erro durante a consulta: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
