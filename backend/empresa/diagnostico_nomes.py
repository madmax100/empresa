#!/usr/bin/env python
"""
🔍 DIAGNÓSTICO DO PROBLEMA DOS NOMES DE PRODUTOS
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import MovimentacoesEstoque, Produtos
from django.db.models import Sum, Q, Count, Case, When, F, DecimalField
from datetime import date, datetime
from decimal import Decimal
import json

def diagnostico_nomes_produtos():
    """Diagnóstico do problema dos nomes de produtos"""
    
    print("=" * 70)
    print("🔍 DIAGNÓSTICO DO PROBLEMA DOS NOMES DE PRODUTOS")
    print("=" * 70)
    
    # 1. Verificar produtos sem descrição
    print("\n📋 VERIFICANDO PRODUTOS SEM DESCRIÇÃO:")
    produtos_sem_descricao = Produtos.objects.filter(
        Q(descricao__isnull=True) | Q(descricao='') | Q(descricao='Produto não identificado')
    ).count()
    print(f"  ❌ Produtos sem descrição: {produtos_sem_descricao}")
    
    # 2. Verificar produtos com descrição válida
    produtos_com_descricao = Produtos.objects.exclude(
        Q(descricao__isnull=True) | Q(descricao='')
    ).count()
    print(f"  ✅ Produtos com descrição: {produtos_com_descricao}")
    
    # 3. Verificar movimentações e nomes
    print(f"\n🔄 VERIFICANDO MOVIMENTAÇÕES:")
    movimentacoes_com_produto = MovimentacoesEstoque.objects.filter(
        produto__isnull=False
    ).count()
    print(f"  ✅ Movimentações com produto: {movimentacoes_com_produto}")
    
    # 4. Testar consulta do endpoint
    print(f"\n🎯 TESTANDO CONSULTA DO ENDPOINT:")
    data_posicao = date.today()
    
    try:
        saldos = MovimentacoesEstoque.objects.filter(
            data_movimentacao__date__lte=data_posicao,
            produto__isnull=False
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
        ).order_by('produto__descricao')
        
        print(f"  ✅ Consulta executada com sucesso")
        print(f"  📊 Total de produtos: {saldos.count()}")
        
        # 5. Verificar primeiros resultados
        print(f"\n📦 PRIMEIROS 10 PRODUTOS:")
        count = 0
        for saldo in saldos[:10]:
            if saldo['saldo_final'] and saldo['saldo_final'] > 0:
                count += 1
                descricao = saldo['produto__descricao'] or 'DESCRIÇÃO NULA'
                print(f"  {count}. ID: {saldo['produto_id']} | "
                      f"Descrição: '{descricao}' | "
                      f"Saldo: {saldo['saldo_final']}")
                
                if descricao == 'DESCRIÇÃO NULA' or not descricao.strip():
                    print(f"      ❌ PROBLEMA: Produto {saldo['produto_id']} sem descrição!")
        
        # 6. Verificar produtos específicos sem descrição
        print(f"\n🔍 VERIFICANDO PRODUTOS PROBLEMÁTICOS:")
        produtos_problematicos = Produtos.objects.filter(
            Q(descricao__isnull=True) | Q(descricao='') | Q(descricao__exact='Produto não identificado')
        ).values('id', 'codigo', 'descricao', 'nome')[:5]
        
        for produto in produtos_problematicos:
            print(f"  ❌ ID: {produto['id']} | "
                  f"Código: {produto.get('codigo', 'N/A')} | "
                  f"Nome: {produto.get('nome', 'N/A')} | "
                  f"Descrição: '{produto.get('descricao', 'NULO')}'")
        
        # 7. Sugerir correção
        print(f"\n🔧 SUGESTÃO DE CORREÇÃO:")
        print(f"  1. Atualizar produtos sem descrição para usar o campo 'nome'")
        print(f"  2. Ou criar uma descrição padrão baseada no código")
        print(f"  3. Verificar se o frontend está lendo o campo correto")
        
    except Exception as e:
        print(f"  ❌ Erro na consulta: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n" + "=" * 70)

if __name__ == "__main__":
    diagnostico_nomes_produtos()
