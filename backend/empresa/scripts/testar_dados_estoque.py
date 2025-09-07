#!/usr/bin/env python3
"""
Script para testar dados diretamente usando Django ORM
"""

import os
import sys
import django
from datetime import datetime, date

# Configurar Django
sys.path.append('c:/Users/Cirilo/Documents/c3mcopias/backend/empresa')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from django.db.models import Sum, Case, When, F, DecimalField
from contas.models import MovimentacoesEstoque, SaldosEstoque, Produtos

def testar_dados_estoque():
    """Testa os dados do estoque diretamente via ORM"""
    print("=== TESTE DOS DADOS DE ESTOQUE VIA ORM ===")
    
    # 1. Teste do relatório de valor do estoque (simulando endpoint)
    print("\n1. 📊 Simulando /api/relatorio-valor-estoque/")
    
    try:
        data_posicao = date.today()
        
        # Calcular saldos como o endpoint faz
        saldos = MovimentacoesEstoque.objects.filter(
            data_movimentacao__date__lte=data_posicao
        ).values(
            'produto_id', 
            'produto__descricao', 
            'produto__preco_custo'
        ).annotate(
            saldo_final=Sum(
                Case(
                    When(tipo_movimentacao__tipo='E', then=F('quantidade')),
                    When(tipo_movimentacao__tipo='S', then=-F('quantidade')),
                    default=0,
                    output_field=DecimalField()
                )
            )
        ).filter(
            saldo_final__gt=0
        ).order_by('produto__descricao')
        
        # Calcular valor total
        valor_total_estoque = 0
        produtos_em_estoque = 0
        
        for saldo in saldos:
            if saldo['saldo_final'] > 0:
                custo = saldo['produto__preco_custo'] or 0
                valor_produto = saldo['saldo_final'] * custo
                valor_total_estoque += valor_produto
                produtos_em_estoque += 1
        
        print(f"   ✅ Dados calculados com sucesso!")
        print(f"   📊 Data da posição: {data_posicao}")
        print(f"   💰 Valor total: R$ {valor_total_estoque:,.2f}")
        print(f"   📦 Produtos em estoque: {produtos_em_estoque}")
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 2. Teste dos saldos diretos
    print("\n2. 📋 Testando SaldosEstoque diretamente")
    
    try:
        saldos_diretos = SaldosEstoque.objects.filter(quantidade__gt=0)
        total_saldos = saldos_diretos.count()
        
        # Calcular valor pelos saldos diretos
        valor_direto = 0
        for saldo in saldos_diretos:
            if saldo.produto_id:
                custo = saldo.custo_medio or saldo.produto_id.preco_custo or 0
                valor_direto += saldo.quantidade * custo
        
        print(f"   ✅ Saldos diretos obtidos!")
        print(f"   📦 Produtos com saldo: {total_saldos}")
        print(f"   💰 Valor pelos saldos: R$ {valor_direto:,.2f}")
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 3. Teste das movimentações
    print("\n3. 🔄 Testando MovimentacoesEstoque")
    
    try:
        # Movimentações de 2025
        movs_2025 = MovimentacoesEstoque.objects.filter(
            data_movimentacao__year=2025
        )
        
        # Por tipo
        from django.db.models import Count
        por_tipo = movs_2025.values(
            'tipo_movimentacao__codigo',
            'tipo_movimentacao__descricao'
        ).annotate(
            total=Count('id')
        ).order_by('-total')
        
        print(f"   ✅ Movimentações de 2025: {movs_2025.count()}")
        print("   📋 Por tipo:")
        for tipo in por_tipo:
            if tipo['tipo_movimentacao__codigo']:
                print(f"     {tipo['tipo_movimentacao__codigo']}: {tipo['total']}")
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 4. Teste de consistência
    print("\n4. ✅ Teste de Consistência")
    
    print(f"   📊 Comparação de valores:")
    print(f"     Via movimentações: R$ {valor_total_estoque:,.2f}")
    print(f"     Via saldos diretos: R$ {valor_direto:,.2f}")
    
    diferenca = abs(valor_total_estoque - valor_direto)
    if diferenca < 1:  # Diferença menor que R$ 1,00
        print(f"   ✅ Valores consistentes (diferença: R$ {diferenca:.2f})")
    else:
        print(f"   ⚠️  Diferença encontrada: R$ {diferenca:.2f}")
    
    print("\n✅ TESTE CONCLUÍDO - DADOS OPERACIONAIS!")

if __name__ == '__main__':
    testar_dados_estoque()
