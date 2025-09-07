#!/usr/bin/env python
"""
Script para recalcular e atualizar saldos de estoque
Calcula saldos baseado nas movimentações registradas
"""

import os
import sys
import django
from datetime import datetime
from decimal import Decimal
from django.db.models import Sum, Case, When, F, Q
from django.db import transaction

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

def verificar_tipos_movimentacao():
    """Verifica os tipos de movimentação disponíveis"""
    print("TIPOS DE MOVIMENTAÇÃO CADASTRADOS")
    print("-" * 50)
    
    tipos = TiposMovimentacaoEstoque.objects.all()
    
    for tipo in tipos:
        print(f"Código: {tipo.codigo} | Descrição: {tipo.descricao} | Tipo: {tipo.tipo}")
    
    print(f"\nTotal: {tipos.count()} tipos")
    print()

def analisar_movimentacoes_sem_saldo():
    """Analisa produtos com movimentações mas sem saldo"""
    print("ANÁLISE: PRODUTOS COM MOVIMENTAÇÕES SEM SALDO")
    print("-" * 60)
    
    # Produtos que têm movimentações
    produtos_com_mov = MovimentacoesEstoque.objects.values('produto_id').distinct()
    produtos_com_mov_ids = [p['produto_id'] for p in produtos_com_mov if p['produto_id']]
    
    # Produtos que têm saldo
    produtos_com_saldo = SaldosEstoque.objects.values('produto_id').distinct()
    produtos_com_saldo_ids = [p['produto_id'] for p in produtos_com_saldo if p['produto_id']]
    
    print(f"Produtos com movimentações: {len(produtos_com_mov_ids)}")
    print(f"Produtos com saldo registrado: {len(produtos_com_saldo_ids)}")
    
    # Produtos com movimentação mas sem saldo
    sem_saldo = set(produtos_com_mov_ids) - set(produtos_com_saldo_ids)
    print(f"Produtos com movimentações mas SEM saldo: {len(sem_saldo)}")
    
    if sem_saldo:
        print("\nPrimeiros 10 produtos sem saldo:")
        produtos_sem_saldo = Produtos.objects.filter(id__in=list(sem_saldo)[:10])
        for produto in produtos_sem_saldo:
            print(f"  {produto.codigo} - {produto.nome}")
    
    print()

def calcular_saldo_produto(produto_id, local_id=None):
    """Calcula saldo de um produto baseado nas movimentações"""
    
    movimentacoes = MovimentacoesEstoque.objects.filter(
        produto_id=produto_id
    ).select_related('tipo_movimentacao')
    
    if local_id:
        # Considera movimentações que afetam o local específico
        movimentacoes = movimentacoes.filter(
            Q(local_destino_id=local_id) | Q(local_origem_id=local_id)
        )
    
    saldo = Decimal('0')
    valor_total = Decimal('0')
    count_movs = 0
    ultima_mov = None
    custos = []
    
    for mov in movimentacoes:
        count_movs += 1
        ultima_mov = mov.data_movimentacao
        
        if mov.tipo_movimentacao:
            if mov.tipo_movimentacao.tipo == 'E':  # Entrada
                saldo += mov.quantidade
                if mov.custo_unitario:
                    custos.append(mov.custo_unitario)
            elif mov.tipo_movimentacao.tipo == 'S':  # Saída
                saldo -= mov.quantidade
    
    # Calcula custo médio
    custo_medio = sum(custos) / len(custos) if custos else None
    
    return {
        'saldo': saldo,
        'custo_medio': custo_medio,
        'ultima_movimentacao': ultima_mov,
        'total_movimentacoes': count_movs
    }

def recalcular_saldos(limite_produtos=100, criar_saldos=False):
    """Recalcula saldos para produtos com movimentações"""
    print(f"RECALCULANDO SALDOS (limite: {limite_produtos} produtos)")
    print("-" * 60)
    
    # Busca produtos com movimentações
    produtos_com_mov = MovimentacoesEstoque.objects.values('produto_id').distinct()[:limite_produtos]
    produtos_ids = [p['produto_id'] for p in produtos_com_mov if p['produto_id']]
    
    print(f"Processando {len(produtos_ids)} produtos...")
    
    saldos_atualizados = 0
    saldos_criados = 0
    erros = 0
    
    with transaction.atomic():
        for produto_id in produtos_ids:
            try:
                # Calcula saldo
                resultado = calcular_saldo_produto(produto_id)
                
                if resultado['saldo'] != 0 or criar_saldos:
                    # Busca ou cria saldo
                    saldo_obj, criado = SaldosEstoque.objects.get_or_create(
                        produto_id_id=produto_id,
                        defaults={
                            'quantidade': resultado['saldo'],
                            'custo_medio': resultado['custo_medio'],
                            'ultima_movimentacao': resultado['ultima_movimentacao']
                        }
                    )
                    
                    if not criado:
                        # Atualiza existente
                        saldo_obj.quantidade = resultado['saldo']
                        if resultado['custo_medio']:
                            saldo_obj.custo_medio = resultado['custo_medio']
                        if resultado['ultima_movimentacao']:
                            saldo_obj.ultima_movimentacao = resultado['ultima_movimentacao']
                        saldo_obj.save()
                        saldos_atualizados += 1
                    else:
                        saldos_criados += 1
                        
            except Exception as e:
                erros += 1
                print(f"Erro no produto {produto_id}: {str(e)}")
    
    print(f"\nResultados:")
    print(f"  Saldos criados: {saldos_criados}")
    print(f"  Saldos atualizados: {saldos_atualizados}")
    print(f"  Erros: {erros}")
    print()

def verificar_produtos_com_saldo_positivo():
    """Verifica produtos que ficaram com saldo positivo"""
    print("PRODUTOS COM SALDO POSITIVO APÓS RECÁLCULO")
    print("-" * 60)
    
    saldos_positivos = SaldosEstoque.objects.filter(
        quantidade__gt=0
    ).select_related('produto_id').order_by('-quantidade')[:20]
    
    print(f"{'Código':<15} {'Nome':<30} {'Qtd':<10} {'Custo Médio':<12} {'Valor':<12}")
    print("-" * 60)
    
    for saldo in saldos_positivos:
        produto = saldo.produto_id
        quantidade = saldo.quantidade
        custo = saldo.custo_medio or Decimal('0')
        valor = quantidade * custo
        
        print(f"{produto.codigo:<15} {produto.nome[:30]:<30} {quantidade:<10} R$ {custo:<10.2f} R$ {valor:<10.2f}")
    
    print(f"\nTotal de produtos com saldo positivo: {SaldosEstoque.objects.filter(quantidade__gt=0).count()}")
    print()

def main():
    """Função principal"""
    try:
        print(f"Recálculo de saldos executado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print()
        
        # Verificações
        verificar_tipos_movimentacao()
        analisar_movimentacoes_sem_saldo()
        
        # Pergunta se deve recalcular
        print("Deseja recalcular os saldos? (Digite 'sim' para confirmar)")
        resposta = input().strip().lower()
        
        if resposta in ['sim', 's', 'yes', 'y']:
            recalcular_saldos(limite_produtos=1000, criar_saldos=True)
            verificar_produtos_com_saldo_positivo()
        else:
            print("Recálculo cancelado pelo usuário.")
        
        print("=" * 60)
        print("VERIFICAÇÃO FINALIZADA")
        print("=" * 60)
        
    except Exception as e:
        print(f"Erro durante a verificação: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
