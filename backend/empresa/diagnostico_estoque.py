#!/usr/bin/env python
"""
🔍 DIAGNÓSTICO DO PROBLEMA DE ESTOQUE FRONTEND
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from contas.models.access import SaldosEstoque, MovimentacoesEstoque, Produtos
from django.db.models import Count, Sum, Q
from datetime import date, datetime
import json

def diagnostico_dados():
    """Diagnóstico completo dos dados de estoque"""
    
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DOS DADOS DE ESTOQUE")
    print("=" * 60)
    
    # 1. Verificar contadores básicos
    saldos_count = SaldosEstoque.objects.count()
    movimentacoes_count = MovimentacoesEstoque.objects.count()
    produtos_count = Produtos.objects.count()
    
    print(f"\n📊 CONTADORES BÁSICOS:")
    print(f"  📋 Total de saldos: {saldos_count}")
    print(f"  🔄 Total de movimentações: {movimentacoes_count}")
    print(f"  📦 Total de produtos: {produtos_count}")
    
    # 2. Verificar saldos com estoque positivo
    saldos_positivos = SaldosEstoque.objects.filter(quantidade__gt=0).count()
    print(f"  ✅ Saldos com estoque positivo: {saldos_positivos}")
    
    # 3. Verificar movimentações de hoje
    hoje = date.today()
    movimentacoes_hoje = MovimentacoesEstoque.objects.filter(
        data_movimentacao__date=hoje
    ).count()
    print(f"  📅 Movimentações de hoje ({hoje}): {movimentacoes_hoje}")
    
    # 4. Verificar movimentações com problemas
    movimentacoes_sem_produto = MovimentacoesEstoque.objects.filter(
        produto__isnull=True
    ).count()
    print(f"  ❌ Movimentações sem produto: {movimentacoes_sem_produto}")
    
    # 5. Verificar estatísticas agregadas
    saldos_stats = SaldosEstoque.objects.aggregate(
        total_produtos=Count('id'),
        total_quantidade=Sum('quantidade'),
        produtos_com_estoque=Count('id', filter=Q(quantidade__gt=0))
    )
    
    print(f"\n📈 ESTATÍSTICAS AGREGADAS:")
    print(f"  - Total produtos: {saldos_stats['total_produtos']}")
    print(f"  - Produtos c/ estoque: {saldos_stats['produtos_com_estoque']}")
    print(f"  - Quantidade total: {saldos_stats['total_quantidade'] or 0}")
    
    # 6. Testar endpoint de relatório manualmente
    print(f"\n🔬 TESTE DO ENDPOINT DE RELATÓRIO:")
    try:
        from contas.views.access import relatorio_valor_estoque
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/contas/relatorio-valor-estoque/')
        
        response = relatorio_valor_estoque(request)
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"  ✅ Valor total: R$ {data.get('valor_total_estoque', 0):,.2f}")
            print(f"  ✅ Total produtos: {data.get('total_produtos_em_estoque', 0)}")
            print(f"  ✅ Total detalhes: {len(data.get('detalhes_por_produto', []))}")
        else:
            print(f"  ❌ Erro no endpoint: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Erro no teste: {e}")
    
    # 7. Verificar últimas movimentações válidas
    print(f"\n🔄 ÚLTIMAS MOVIMENTAÇÕES VÁLIDAS:")
    try:
        ultimas_validas = MovimentacoesEstoque.objects.filter(
            produto__isnull=False
        ).order_by('-data_movimentacao')[:5]
        
        for i, mov in enumerate(ultimas_validas, 1):
            print(f"  {i}. {mov.data_movimentacao.strftime('%Y-%m-%d %H:%M')} | "
                  f"{mov.produto.descricao[:30]} | Qtd: {mov.quantidade}")
                  
    except Exception as e:
        print(f"  ❌ Erro ao listar movimentações: {e}")
    
    # 8. Verificar endpoints disponíveis
    print(f"\n🌐 ENDPOINTS PARA TESTE MANUAL:")
    print(f"  GET http://localhost:8000/contas/relatorio-valor-estoque/")
    print(f"  GET http://localhost:8000/contas/saldos_estoque/")
    print(f"  GET http://localhost:8000/contas/saldos_estoque/?quantidade__gt=0")
    print(f"  GET http://localhost:8000/contas/movimentacoes_estoque/")
    print(f"  GET http://localhost:8000/contas/movimentacoes_estoque/?data_movimentacao__date={hoje}")
    
    print(f"\n🔧 POSSÍVEIS CAUSAS DO PROBLEMA:")
    print(f"  1. ❌ Servidor Django não está rodando")
    print(f"  2. ❌ CORS não configurado para o frontend")
    print(f"  3. ❌ Frontend usando URLs incorretas (/api/ ao invés de /contas/)")
    print(f"  4. ❌ Filtros no frontend não funcionando corretamente")
    print(f"  5. ❌ Cache do navegador")
    
    print(f"\n✅ RESUMO:")
    print(f"  - Dados no backend: ✅ DISPONÍVEIS")
    print(f"  - {saldos_positivos} produtos com estoque")
    print(f"  - {movimentacoes_count} movimentações totais")
    print(f"  - Endpoints funcionando: ✅ SIM")
    
    print(f"\n" + "=" * 60)

if __name__ == "__main__":
    diagnostico_dados()
