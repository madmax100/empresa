#!/usr/bin/env python
"""
🔧 TESTE DETALHADO DO ENDPOINT DE RELATÓRIO
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
import traceback

def teste_detalhado_endpoint():
    """Teste detalhado para encontrar o problema específico"""
    
    print("=" * 60)
    print("🔧 TESTE DETALHADO DO ENDPOINT DE RELATÓRIO")
    print("=" * 60)
    
    try:
        # 1. Testar parâmetros
        data_posicao_str = date.today().strftime('%Y-%m-%d')
        data_posicao = datetime.strptime(data_posicao_str, '%Y-%m-%d').date()
        print(f"✅ Data de posição: {data_posicao}")
        
        # 2. Testar consulta básica
        print(f"\n🔍 Testando consulta básica...")
        movimentacoes_total = MovimentacoesEstoque.objects.count()
        print(f"✅ Total de movimentações: {movimentacoes_total}")
        
        # 3. Testar filtro por data
        print(f"\n📅 Testando filtro por data...")
        movimentacoes_ate_data = MovimentacoesEstoque.objects.filter(
            data_movimentacao__date__lte=data_posicao
        ).count()
        print(f"✅ Movimentações até {data_posicao}: {movimentacoes_ate_data}")
        
        # 4. Testar join com produtos
        print(f"\n🔗 Testando join com produtos...")
        movimentacoes_com_produto = MovimentacoesEstoque.objects.filter(
            data_movimentacao__date__lte=data_posicao,
            produto__isnull=False
        ).count()
        print(f"✅ Movimentações com produto: {movimentacoes_com_produto}")
        
        # 5. Testar values específicos
        print(f"\n📊 Testando values...")
        try:
            saldos_teste = MovimentacoesEstoque.objects.filter(
                data_movimentacao__date__lte=data_posicao,
                produto__isnull=False
            ).values(
                'produto_id', 
                'produto__descricao', 
                'produto__custo'
            )[:5]
            
            print(f"✅ Values funcionando. Primeiros 5 registros:")
            for saldo in saldos_teste:
                print(f"  - Produto {saldo['produto_id']}: {saldo['produto__descricao'][:30]}")
                
        except Exception as e:
            print(f"❌ Erro no values: {e}")
            traceback.print_exc()
        
        # 6. Testar annotate
        print(f"\n🧮 Testando annotate...")
        try:
            saldos_annotate = MovimentacoesEstoque.objects.filter(
                data_movimentacao__date__lte=data_posicao,
                produto__isnull=False
            ).values(
                'produto_id'
            ).annotate(
                saldo_final=Sum(
                    Case(
                        When(tipo_movimentacao__tipo='E', then=F('quantidade')),
                        When(tipo_movimentacao__tipo='S', then=-F('quantidade')),
                        default=0,
                        output_field=DecimalField()
                    )
                )
            )[:5]
            
            print(f"✅ Annotate funcionando. Primeiros 5 saldos:")
            for saldo in saldos_annotate:
                print(f"  - Produto {saldo['produto_id']}: Saldo {saldo['saldo_final']}")
                
        except Exception as e:
            print(f"❌ Erro no annotate: {e}")
            traceback.print_exc()
        
        # 7. Testar a consulta completa
        print(f"\n🎯 Testando consulta completa...")
        try:
            saldos_completo = MovimentacoesEstoque.objects.filter(
                data_movimentacao__date__lte=data_posicao,
                produto__isnull=False
            ).values(
                'produto_id', 
                'produto__descricao', 
                'produto__custo'
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
            
            print(f"✅ Consulta completa funcionando!")
            print(f"✅ Total de produtos com movimentações: {saldos_completo.count()}")
            
            # Testar iteração
            valor_total = Decimal('0.00')
            produtos_com_estoque = 0
            
            for saldo in saldos_completo[:10]:  # Apenas primeiros 10
                if saldo['saldo_final'] and saldo['saldo_final'] > 0:
                    custo = saldo['produto__custo'] or Decimal('0.00')
                    valor_produto = saldo['saldo_final'] * custo
                    valor_total += valor_produto
                    produtos_com_estoque += 1
                    
                    print(f"  - {saldo['produto__descricao'][:30]}: {saldo['saldo_final']} x R$ {custo} = R$ {valor_produto}")
            
            print(f"\n💰 Valor total (primeiros 10): R$ {valor_total:,.2f}")
            print(f"📦 Produtos com estoque (primeiros 10): {produtos_com_estoque}")
            
        except Exception as e:
            print(f"❌ Erro na consulta completa: {e}")
            traceback.print_exc()
        
        print(f"\n✅ TESTE CONCLUÍDO!")
        
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    teste_detalhado_endpoint()
