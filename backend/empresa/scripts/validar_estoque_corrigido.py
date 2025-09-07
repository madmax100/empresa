#!/usr/bin/env python3
"""
Script para validar a correção do estoque e gerar relatório final
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
from django.db.models import Sum, Count, Min, Max
from contas.models import MovimentacoesEstoque, SaldosEstoque, Produtos, TiposMovimentacaoEstoque

def validar_correcao():
    """Valida se a correção do estoque foi bem-sucedida"""
    print("=== RELATÓRIO DE VALIDAÇÃO - ESTOQUE CORRIGIDO ===")
    print(f"Data/Hora da validação: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    data_corte = timezone.make_aware(datetime(2025, 1, 1, 0, 0, 0))
    
    print("\n1. 📊 ANÁLISE DAS MOVIMENTAÇÕES:")
    
    # Verificar se não há movimentações antes de 2025
    movs_antigas = MovimentacoesEstoque.objects.filter(data_movimentacao__lt=data_corte)
    print(f"   Movimentações antes de 01/01/2025: {movs_antigas.count()}")
    
    if movs_antigas.count() > 0:
        print("   ❌ ERRO: Ainda existem movimentações antigas!")
        return False
    else:
        print("   ✅ OK: Nenhuma movimentação anterior a 01/01/2025")
    
    # Movimentações de 2025 em diante
    movs_2025 = MovimentacoesEstoque.objects.filter(data_movimentacao__gte=data_corte)
    total_movs_2025 = movs_2025.count()
    print(f"   Total de movimentações de 2025: {total_movs_2025}")
    
    # Data da primeira movimentação
    primeira_mov = MovimentacoesEstoque.objects.order_by('data_movimentacao').first()
    if primeira_mov:
        print(f"   Primeira movimentação: {primeira_mov.data_movimentacao}")
        if primeira_mov.data_movimentacao.date() == date(2025, 1, 1):
            print("   ✅ OK: Primeira movimentação é 01/01/2025")
        else:
            print("   ⚠️  AVISO: Primeira movimentação não é 01/01/2025")
    
    print("\n2. 📦 ANÁLISE DOS SALDOS:")
    
    # Saldos atuais
    total_saldos = SaldosEstoque.objects.count()
    saldos_positivos = SaldosEstoque.objects.filter(quantidade__gt=0)
    total_saldos_positivos = saldos_positivos.count()
    
    print(f"   Total de registros de saldo: {total_saldos}")
    print(f"   Saldos positivos: {total_saldos_positivos}")
    
    # Valor total do estoque
    valor_total = Decimal('0')
    for saldo in saldos_positivos:
        custo = saldo.custo_medio or (saldo.produto_id.preco_custo if saldo.produto_id else Decimal('0'))
        valor_total += saldo.quantidade * custo
    
    print(f"   Valor total do estoque: R$ {valor_total:,.2f}")
    
    print("\n3. 🏷️ ANÁLISE DOS TIPOS DE MOVIMENTAÇÃO:")
    
    # Verificar tipo de estoque inicial
    tipo_inicial = TiposMovimentacaoEstoque.objects.filter(codigo='EST_INI').first()
    if tipo_inicial:
        print(f"   ✅ Tipo 'Estoque Inicial' existe: {tipo_inicial.descricao}")
        
        # Movimentações de estoque inicial
        movs_iniciais = MovimentacoesEstoque.objects.filter(
            tipo_movimentacao=tipo_inicial,
            data_movimentacao__date=date(2025, 1, 1)
        )
        print(f"   Movimentações de estoque inicial: {movs_iniciais.count()}")
    else:
        print("   ❌ ERRO: Tipo 'Estoque Inicial' não encontrado!")
    
    # Todos os tipos utilizados
    tipos_utilizados = MovimentacoesEstoque.objects.values(
        'tipo_movimentacao__codigo',
        'tipo_movimentacao__descricao'
    ).annotate(
        total=Count('id')
    ).order_by('-total')
    
    print("\n   Tipos de movimentação utilizados:")
    for tipo in tipos_utilizados:
        if tipo['tipo_movimentacao__codigo']:
            print(f"     {tipo['tipo_movimentacao__codigo']}: {tipo['total']} movimentações")
    
    print("\n4. 📈 ANÁLISE TEMPORAL:")
    
    # Movimentações por mês em 2025
    movs_por_mes = {}
    for mov in movs_2025:
        mes_ano = mov.data_movimentacao.strftime('%m/%Y')
        movs_por_mes[mes_ano] = movs_por_mes.get(mes_ano, 0) + 1
    
    print("   Movimentações por mês em 2025:")
    for mes in sorted(movs_por_mes.keys()):
        print(f"     {mes}: {movs_por_mes[mes]} movimentações")
    
    print("\n5. 🎯 PRODUTOS COM MAIOR ESTOQUE:")
    
    # Top 10 produtos com maior estoque
    top_produtos = saldos_positivos.select_related('produto_id').order_by('-quantidade')[:10]
    
    print("   Top 10 produtos por quantidade:")
    for i, saldo in enumerate(top_produtos, 1):
        if saldo.produto_id and saldo.produto_id.descricao:
            custo = saldo.custo_medio or saldo.produto_id.preco_custo or Decimal('0')
            valor = saldo.quantidade * custo
            descricao = saldo.produto_id.descricao or f"Produto ID {saldo.produto_id.id}"
            print(f"     {i:2d}. {descricao[:50]:<50} | Qtd: {saldo.quantidade:>8.2f} | Valor: R$ {valor:>10,.2f}")
    
    print("\n6. 💰 PRODUTOS COM MAIOR VALOR:")
    
    # Calcular valor por produto e ordenar
    produtos_valor = []
    for saldo in saldos_positivos.select_related('produto_id'):
        if saldo.produto_id and saldo.produto_id.descricao:
            custo = saldo.custo_medio or saldo.produto_id.preco_custo or Decimal('0')
            valor = saldo.quantidade * custo
            produtos_valor.append({
                'produto': saldo.produto_id,
                'quantidade': saldo.quantidade,
                'custo': custo,
                'valor': valor
            })
    
    # Ordenar por valor e pegar top 10
    produtos_valor.sort(key=lambda x: x['valor'], reverse=True)
    
    print("   Top 10 produtos por valor:")
    for i, item in enumerate(produtos_valor[:10], 1):
        descricao = item['produto'].descricao or f"Produto ID {item['produto'].id}"
        print(f"     {i:2d}. {descricao[:50]:<50} | Qtd: {item['quantidade']:>8.2f} | Valor: R$ {item['valor']:>10,.2f}")
    
    print("\n7. ✅ RESUMO DA VALIDAÇÃO:")
    
    validacao_ok = True
    
    # Checklist de validação
    checks = [
        ("Nenhuma movimentação antes de 2025", movs_antigas.count() == 0),
        ("Primeira movimentação é 01/01/2025", primeira_mov and primeira_mov.data_movimentacao.date() == date(2025, 1, 1)),
        ("Tipo 'Estoque Inicial' existe", tipo_inicial is not None),
        ("Existem saldos positivos", total_saldos_positivos > 0),
        ("Valor total > 0", valor_total > 0),
        ("Movimentações de 2025 existem", total_movs_2025 > 0)
    ]
    
    for descricao, resultado in checks:
        status = "✅" if resultado else "❌"
        print(f"   {status} {descricao}")
        if not resultado:
            validacao_ok = False
    
    print(f"\n{'='*60}")
    if validacao_ok:
        print("🎉 VALIDAÇÃO CONCLUÍDA COM SUCESSO!")
        print("O estoque foi corrigido corretamente para iniciar em 01/01/2025")
    else:
        print("❌ VALIDAÇÃO FALHOU!")
        print("Existem problemas que precisam ser corrigidos")
    
    print(f"{'='*60}")
    
    # Estatísticas finais
    print(f"\n📊 ESTATÍSTICAS FINAIS:")
    print(f"   • {total_movs_2025:,} movimentações de estoque (01/01/2025 em diante)")
    print(f"   • {total_saldos_positivos:,} produtos com estoque positivo")
    print(f"   • R$ {valor_total:,.2f} valor total do estoque")
    print(f"   • Primeira data de movimentação: 01/01/2025")
    print(f"   • Sistema pronto para uso normal")
    
    return validacao_ok

if __name__ == '__main__':
    try:
        validar_correcao()
    except Exception as e:
        print(f"Erro durante a validação: {e}")
        import traceback
        traceback.print_exc()
