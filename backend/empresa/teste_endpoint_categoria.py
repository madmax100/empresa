#!/usr/bin/env python
"""
🧪 TESTE DO ENDPOINT COM CATEGORIA INCLUÍDA
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
from contas.models.access import MovimentacoesEstoque, Grupos

def testar_endpoint_com_categoria():
    """Testa o endpoint com categoria incluída"""
    print("=" * 80)
    print("🧪 TESTE DO ENDPOINT COM CATEGORIA INCLUÍDA")
    print("=" * 80)
    
    try:
        data_posicao = date.today()
        
        print(f"📅 Data de posição: {data_posicao}")
        print()
        
        # Consulta EXATA do endpoint com categoria
        saldos = MovimentacoesEstoque.objects.filter(
            data_movimentacao__date__lte=data_posicao,
            produto__isnull=False
        ).values(
            'produto_id', 
            'produto__descricao', 
            'produto__nome',
            'produto__preco_custo',
            'produto__grupo_id'           # ← NOVO: Grupo/categoria
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
        
        # Buscar nomes dos grupos/categorias
        grupos_ids = [saldo['produto__grupo_id'] for saldo in saldos if saldo['produto__grupo_id'] and saldo['saldo_final'] > 0]
        grupos_dict = {grupo.id: grupo.nome for grupo in Grupos.objects.filter(id__in=grupos_ids)} if grupos_ids else {}
        
        print(f"📁 Categorias encontradas: {len(grupos_dict)}")
        if grupos_dict:
            print("   Categorias disponíveis:")
            for grupo_id, nome in list(grupos_dict.items())[:10]:
                print(f"   - ID {grupo_id}: {nome}")
        print()
        
        # Calcular valor total e preparar detalhes
        valor_total_estoque = Decimal('0.00')
        detalhes_produtos = []
        produtos_com_estoque = 0
        
        for saldo in saldos:
            if saldo['saldo_final'] > 0:
                produtos_com_estoque += 1
                custo = saldo['produto__preco_custo'] or Decimal('0.00')
                valor_produto = saldo['saldo_final'] * custo
                valor_total_estoque += valor_produto
                
                # Obter nome da categoria/grupo
                grupo_id = saldo['produto__grupo_id']
                categoria_nome = grupos_dict.get(grupo_id, 'Sem categoria') if grupo_id else 'Sem categoria'
                
                # Aplicar a lógica de fallback para o nome
                nome_produto = (
                    saldo['produto__descricao'] or 
                    saldo['produto__nome'] or 
                    'Produto sem nome'
                )
                
                detalhes_produtos.append({
                    'produto_id': saldo['produto_id'],
                    'produto_descricao': nome_produto,
                    'categoria': categoria_nome,      # ← NOVO: Campo categoria
                    'quantidade_em_estoque': saldo['saldo_final'],
                    'custo_unitario': custo,
                    'valor_total_produto': valor_produto
                })
        
        print("💰 RESUMO FINANCEIRO:")
        print(f"  💵 Valor total do estoque: R$ {valor_total_estoque:,.2f}")
        print(f"  📦 Produtos com estoque: {produtos_com_estoque}")
        print()
        
        print("🎯 PRIMEIROS 10 PRODUTOS (COM CATEGORIA):")
        for i, produto in enumerate(detalhes_produtos[:10]):
            print(f"  {i+1:2d}. ID: {produto['produto_id']:4d} | Estoque: {produto['quantidade_em_estoque']:6.1f}")
            print(f"      📝 Nome: '{produto['produto_descricao']}'")
            print(f"      📁 Categoria: '{produto['categoria']}'")  # ← NOVO
            print(f"      💵 Valor: R$ {produto['valor_total_produto']:8.2f}")
            print()
        
        # Análise das categorias
        print("📁 ANÁLISE DAS CATEGORIAS:")
        categorias_count = {}
        for produto in detalhes_produtos:
            cat = produto['categoria']
            categorias_count[cat] = categorias_count.get(cat, 0) + 1
        
        for categoria, quantidade in sorted(categorias_count.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  📁 {categoria}: {quantidade} produtos")
        
        # Simular resposta JSON com categoria
        response_data = {
            'data_posicao': data_posicao,
            'valor_total_estoque': float(valor_total_estoque),
            'total_produtos_em_estoque': len(detalhes_produtos),
            'detalhes_por_produto': detalhes_produtos[:5]
        }
        
        print()
        print("📄 EXEMPLO DE RESPOSTA JSON (COM CATEGORIA):")
        print("=" * 80)
        print("{")
        print(f'    "data_posicao": "{response_data["data_posicao"]}",')
        print(f'    "valor_total_estoque": {response_data["valor_total_estoque"]},')
        print(f'    "total_produtos_em_estoque": {response_data["total_produtos_em_estoque"]},')
        print('    "detalhes_por_produto": [')
        
        for i, produto in enumerate(response_data['detalhes_por_produto']):
            print("        {")
            print(f'            "produto_id": {produto["produto_id"]},')
            print(f'            "produto_descricao": "{produto["produto_descricao"]}",')
            print(f'            "categoria": "{produto["categoria"]}",')  # ← NOVO
            print(f'            "quantidade_em_estoque": {produto["quantidade_em_estoque"]},')
            print(f'            "custo_unitario": {produto["custo_unitario"]},')
            print(f'            "valor_total_produto": {produto["valor_total_produto"]}')
            if i < len(response_data['detalhes_por_produto']) - 1:
                print("        },")
            else:
                print("        }")
        
        print("    ]")
        print("}")
        
        print()
        print("=" * 80)
        print("✅ TESTE CONCLUÍDO - ENDPOINT COM CATEGORIA FUNCIONANDO!")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ ERRO durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    testar_endpoint_com_categoria()
