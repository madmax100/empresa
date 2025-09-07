#!/usr/bin/env python3
"""
Script para analisar o estado atual do estoque e planejar a correção para 01/01/2025
"""

import os
import sys
import django
from datetime import datetime, date
from decimal import Decimal

# Configurar Django
sys.path.append('c:/Users/Cirilo/Documents/c3mcopias/backend/empresa')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models import MovimentacoesEstoque, SaldosEstoque, Produtos, TiposMovimentacaoEstoque

def analisar_estoque_atual():
    """Analisa o estado atual do estoque"""
    print("=== ANÁLISE DO ESTOQUE ATUAL ===")
    
    # 1. Verificar movimentações existentes
    movimentacoes = MovimentacoesEstoque.objects.all()
    total_movimentacoes = movimentacoes.count()
    print(f"Total de movimentações: {total_movimentacoes}")
    
    if total_movimentacoes > 0:
        # Primeira e última movimentação
        primeira_mov = movimentacoes.order_by('data_movimentacao').first()
        ultima_mov = movimentacoes.order_by('-data_movimentacao').first()
        
        print(f"Primeira movimentação: {primeira_mov.data_movimentacao}")
        print(f"Última movimentação: {ultima_mov.data_movimentacao}")
        
        # Movimentações por ano
        from django.db.models import Count, Q
        from datetime import datetime
        
        movs_por_ano = {}
        for mov in movimentacoes.values_list('data_movimentacao', flat=True):
            ano = mov.year
            movs_por_ano[ano] = movs_por_ano.get(ano, 0) + 1
        
        print("\nMovimentações por ano:")
        for ano in sorted(movs_por_ano.keys()):
            print(f"  {ano}: {movs_por_ano[ano]} movimentações")
        
        # Movimentações anteriores a 2025
        movs_antes_2025 = movimentacoes.filter(
            data_movimentacao__lt=datetime(2025, 1, 1)
        ).count()
        print(f"\nMovimentações antes de 01/01/2025: {movs_antes_2025}")
        
        # Movimentações em 2025
        movs_2025 = movimentacoes.filter(
            data_movimentacao__gte=datetime(2025, 1, 1)
        ).count()
        print(f"Movimentações em 2025: {movs_2025}")
    
    # 2. Verificar saldos atuais
    saldos = SaldosEstoque.objects.all()
    total_saldos = saldos.count()
    print(f"\nTotal de saldos registrados: {total_saldos}")
    
    saldos_positivos = saldos.filter(quantidade__gt=0).count()
    print(f"Saldos positivos: {saldos_positivos}")
    
    # 3. Verificar produtos
    produtos = Produtos.objects.all()
    total_produtos = produtos.count()
    print(f"\nTotal de produtos: {total_produtos}")
    
    produtos_com_saldo = produtos.filter(saldosestoque__quantidade__gt=0).distinct().count()
    print(f"Produtos com saldo positivo: {produtos_com_saldo}")
    
    # 4. Verificar tipos de movimentação
    tipos_mov = TiposMovimentacaoEstoque.objects.all()
    print(f"\nTipos de movimentação disponíveis: {tipos_mov.count()}")
    for tipo in tipos_mov:
        print(f"  {tipo.codigo} - {tipo.descricao} ({tipo.tipo})")
    
    return {
        'total_movimentacoes': total_movimentacoes,
        'movs_antes_2025': movs_antes_2025 if total_movimentacoes > 0 else 0,
        'movs_2025': movs_2025 if total_movimentacoes > 0 else 0,
        'total_saldos': total_saldos,
        'saldos_positivos': saldos_positivos,
        'total_produtos': total_produtos,
        'produtos_com_saldo': produtos_com_saldo
    }

def planejar_correcao():
    """Planeja as correções necessárias"""
    print("\n=== PLANO DE CORREÇÃO ===")
    
    dados = analisar_estoque_atual()
    
    print("1. BACKUP dos dados atuais")
    print("   - Fazer backup das movimentações existentes")
    print("   - Fazer backup dos saldos atuais")
    
    print("\n2. LIMPEZA de movimentações anteriores a 2025")
    if dados['movs_antes_2025'] > 0:
        print(f"   - Remover {dados['movs_antes_2025']} movimentações anteriores a 01/01/2025")
    else:
        print("   - Nenhuma movimentação anterior a 2025 encontrada")
    
    print("\n3. CRIAÇÃO do estoque inicial em 01/01/2025")
    if dados['saldos_positivos'] > 0:
        print(f"   - Criar movimentação de 'Estoque Inicial' para {dados['saldos_positivos']} produtos")
        print("   - Data: 01/01/2025 00:00:00")
        print("   - Tipo: Entrada (Estoque Inicial)")
    else:
        print("   - Nenhum saldo positivo para criar estoque inicial")
    
    print("\n4. ATUALIZAÇÃO dos saldos")
    print("   - Recalcular saldos baseados nas novas movimentações")
    print("   - Manter apenas movimentações de 01/01/2025 em diante")
    
    print("\n5. VALIDAÇÃO")
    print("   - Verificar se os saldos finais coincidem com os saldos atuais")
    print("   - Verificar se não há movimentações anteriores a 01/01/2025")

if __name__ == '__main__':
    try:
        analisar_estoque_atual()
        planejar_correcao()
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()
