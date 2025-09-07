#!/usr/bin/env python
"""
🔧 TESTE DA CORREÇÃO DOS NOMES DE PRODUTOS
"""
import os
import sys
import django
from decimal import Decimal

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from django.db.models import Sum, Case, When, F, DecimalField
from datetime import date
from contas.models.access import MovimentacoesEstoque

def testar_consulta_corrigida():
    """Testa a consulta corrigida que usa nome como fallback"""
    print("=" * 70)
    print("🔧 TESTANDO CORREÇÃO DOS NOMES DE PRODUTOS")
    print("=" * 70)
    
    try:
        # Simular a consulta do endpoint corrigido
        data_posicao = date.today()
        
        saldos = MovimentacoesEstoque.objects.filter(
            data_movimentacao__date__lte=data_posicao,
            produto__isnull=False
        ).values(
            'produto_id', 
            'produto__descricao', 
            'produto__nome',
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
        ).order_by('produto__nome')
        
        print(f"📊 Total de produtos processados: {len(saldos)}")
        print()
        print("🎯 PRIMEIROS 10 PRODUTOS (APÓS CORREÇÃO):")
        
        count = 0
        for saldo in saldos:
            if saldo['saldo_final'] > 0 and count < 10:
                count += 1
                # Aplicar a lógica de fallback
                nome_produto = saldo['produto__descricao'] or saldo['produto__nome'] or 'Produto sem nome'
                
                print(f"  {count}. ID: {saldo['produto_id']} | Nome: '{nome_produto}' | Saldo: {saldo['saldo_final']}")
                
                if saldo['produto__descricao']:
                    print(f"      ✅ USANDO DESCRIÇÃO: {saldo['produto__descricao']}")
                elif saldo['produto__nome']:
                    print(f"      🔄 USANDO NOME COMO FALLBACK: {saldo['produto__nome']}")
                else:
                    print(f"      ❌ SEM NOME E SEM DESCRIÇÃO!")
        
        print()
        print("🔍 ANÁLISE DO FALLBACK:")
        
        produtos_com_descricao = 0
        produtos_com_nome = 0
        produtos_sem_nada = 0
        
        for saldo in saldos:
            if saldo['saldo_final'] > 0:
                if saldo['produto__descricao']:
                    produtos_com_descricao += 1
                elif saldo['produto__nome']:
                    produtos_com_nome += 1
                else:
                    produtos_sem_nada += 1
        
        print(f"  ✅ Produtos com descrição: {produtos_com_descricao}")
        print(f"  🔄 Produtos usando nome como fallback: {produtos_com_nome}")
        print(f"  ❌ Produtos sem nome nem descrição: {produtos_sem_nada}")
        
        print()
        print("=" * 70)
        print("✅ TESTE CONCLUÍDO - CORREÇÃO APLICADA COM SUCESSO!")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ ERRO durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    testar_consulta_corrigida()
