#!/usr/bin/env python3
"""
Script de SIMULAÇÃO para corrigir o estoque iniciando em 01/01/2025
Este script apenas simula as operações sem modificar os dados
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

from django.utils import timezone
from contas.models import MovimentacoesEstoque, SaldosEstoque, Produtos, TiposMovimentacaoEstoque

def simular_correcao():
    """Simula a correção do estoque sem modificar dados"""
    print("=== SIMULAÇÃO DE CORREÇÃO DO ESTOQUE ===")
    print("Este é um modo de simulação - nenhum dado será modificado")
    
    data_corte = timezone.make_aware(datetime(2025, 1, 1, 0, 0, 0))
    
    # 1. Analisar situação atual
    print("\n1. SITUAÇÃO ATUAL:")
    total_movs = MovimentacoesEstoque.objects.count()
    movs_antes_2025 = MovimentacoesEstoque.objects.filter(data_movimentacao__lt=data_corte).count()
    movs_2025 = MovimentacoesEstoque.objects.filter(data_movimentacao__gte=data_corte).count()
    
    print(f"   Total de movimentações: {total_movs}")
    print(f"   Movimentações antes de 2025: {movs_antes_2025}")
    print(f"   Movimentações de 2025: {movs_2025}")
    
    # 2. Saldos atuais
    print("\n2. SALDOS ATUAIS:")
    saldos_positivos = SaldosEstoque.objects.filter(quantidade__gt=0)
    total_saldos_positivos = saldos_positivos.count()
    
    print(f"   Produtos com saldo positivo: {total_saldos_positivos}")
    
    # Calcular valor total
    valor_total = sum(
        saldo.quantidade * (saldo.custo_medio or saldo.produto_id.preco_custo or Decimal('0'))
        for saldo in saldos_positivos
        if saldo.produto_id
    )
    
    print(f"   Valor total do estoque: R$ {valor_total:,.2f}")
    
    # 3. Operações que seriam realizadas
    print("\n3. OPERAÇÕES QUE SERIAM REALIZADAS:")
    print(f"   ❌ Remover {movs_antes_2025} movimentações anteriores a 01/01/2025")
    print(f"   ✅ Criar {total_saldos_positivos} movimentações de 'Estoque Inicial' em 01/01/2025")
    print(f"   🔄 Recalcular saldos baseados nas novas movimentações")
    print(f"   ✅ Manter {movs_2025} movimentações existentes de 2025")
    
    # 4. Validar se seria possível
    print("\n4. VALIDAÇÕES:")
    
    tipos_mov = TiposMovimentacaoEstoque.objects.filter(codigo='EST_INI')
    if tipos_mov.exists():
        print("   ✅ Tipo 'Estoque Inicial' já existe")
    else:
        print("   ➕ Tipo 'Estoque Inicial' seria criado")
    
    if total_saldos_positivos > 0:
        print(f"   ✅ {total_saldos_positivos} produtos têm saldo positivo para migrar")
    else:
        print("   ❌ ERRO: Nenhum produto com saldo positivo!")
        return False
    
    # 5. Resultado esperado
    print("\n5. RESULTADO ESPERADO:")
    print(f"   📅 Primeira movimentação: 01/01/2025 00:00:00")
    print(f"   📊 Produtos com estoque: {total_saldos_positivos}")
    print(f"   💰 Valor total preservado: R$ {valor_total:,.2f}")
    print(f"   🗂️ Histórico limpo: apenas movimentações de 2025 em diante")
    
    print("\n✅ SIMULAÇÃO CONCLUÍDA")
    print("Para executar a correção real, use o script 'corrigir_estoque_2025.py'")
    
    return True

if __name__ == '__main__':
    simular_correcao()
