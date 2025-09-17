#!/usr/bin/env python3
"""
Script para testar e implementar o endpoint de produtos resetados
"""

import os
import sys
import django

# Configurar Django
sys.path.append('backend/empresa')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'empresa.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from collections import defaultdict
from contas.models.access import MovimentacoesEstoque, Produtos, Grupos

def testar_produtos_resetados():
    """Testar a lógica do endpoint produtos_resetados"""
    
    print("=== TESTE: PRODUTOS RESETADOS NO ÚLTIMO ANO ===\n")
    
    # Data limite para buscar resets (últimos 12 meses)
    data_limite = timezone.now().date() - timedelta(days=12 * 30)
    print(f"Buscando resets desde: {data_limite}")
    
    # Buscar movimentações de reset no período
    resets_query = MovimentacoesEstoque.objects.filter(
        documento_referencia='000000',
        data_movimentacao__gte=data_limite
    )
    
    print(f"Total de resets encontrados: {resets_query.count()}")
    
    # Agrupar por produto e pegar o reset mais recente de cada um
    produtos_resetados = {}
    
    for reset in resets_query:
        produto_id = reset.produto_id
        
        if produto_id not in produtos_resetados or reset.data_movimentacao.date() > produtos_resetados[produto_id]['data_reset']:
            try:
                produto = Produtos.objects.get(id=produto_id)
                grupo = produto.grupo_id
                grupo_nome = ''
                
                if grupo:
                    try:
                        grupo_obj = Grupos.objects.get(id=grupo)
                        grupo_nome = grupo_obj.nome
                    except Grupos.DoesNotExist:
                        grupo_nome = f'Grupo {grupo}'
                
                produtos_resetados[produto_id] = {
                    'produto_id': produto_id,
                    'codigo': produto.codigo,
                    'nome': produto.nome,
                    'grupo_id': grupo,
                    'grupo_nome': grupo_nome or 'Sem Grupo',
                    'data_reset': reset.data_movimentacao.date(),
                    'quantidade_reset': float(reset.quantidade or 0),
                    'estoque_atual': float(produto.estoque_atual or 0),
                    'preco_custo': float(produto.preco_custo or 0),
                    'valor_atual': float((produto.estoque_atual or 0) * (produto.preco_custo or 0)),
                    'ativo': produto.ativo
                }
            except Produtos.DoesNotExist:
                continue
    
    # Converter para lista e ordenar por data de reset
    produtos_list = list(produtos_resetados.values())
    produtos_list.sort(key=lambda x: x['data_reset'], reverse=True)
    
    print(f"Produtos únicos com reset: {len(produtos_list)}")
    
    # Mostrar os primeiros 10
    print("\nPrimeiros 10 produtos resetados:")
    print("-" * 120)
    print(f"{'Código':<10} {'Nome':<40} {'Grupo':<20} {'Data Reset':<12} {'Qtd Reset':<10} {'Estoque Atual':<15}")
    print("-" * 120)
    
    for produto in produtos_list[:10]:
        print(f"{produto['codigo']:<10} {produto['nome'][:38]:<40} {produto['grupo_nome'][:18]:<20} "
              f"{produto['data_reset']:<12} {produto['quantidade_reset']:<10} {produto['estoque_atual']:<15}")
    
    # Estatísticas
    total_valor = sum(p['valor_atual'] for p in produtos_list)
    produtos_ativos = sum(1 for p in produtos_list if p['ativo'])
    produtos_com_estoque = sum(1 for p in produtos_list if p['estoque_atual'] > 0)
    
    print(f"\n=== ESTATÍSTICAS ===")
    print(f"Total de produtos resetados: {len(produtos_list)}")
    print(f"Produtos ativos: {produtos_ativos}")
    print(f"Produtos com estoque atual: {produtos_com_estoque}")
    print(f"Valor total do estoque atual: R$ {total_valor:,.2f}")
    
    # Agrupar por mês de reset
    resets_por_mes = defaultdict(int)
    for produto in produtos_list:
        mes_ano = produto['data_reset'].strftime('%Y-%m')
        resets_por_mes[mes_ano] += 1
    
    print(f"\nResets por mês:")
    for mes, count in sorted(resets_por_mes.items()):
        print(f"  {mes}: {count} produtos")

if __name__ == "__main__":
    testar_produtos_resetados()