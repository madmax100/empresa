
# views/estoque_otimizado.py
from django.core.cache import cache
from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, date
from decimal import Decimal

@api_view(['GET'])
def relatorio_valor_estoque_otimizado(request):
    """
    Versão otimizada do relatório de estoque por data
    """
    try:
        # 1. Parâmetros
        data_str = request.query_params.get('data', date.today().strftime('%Y-%m-%d'))
        data_posicao = datetime.strptime(data_str, '%Y-%m-%d').date()
        usar_cache = request.query_params.get('cache', 'true').lower() == 'true'
        
        # 2. Verificar cache primeiro
        cache_key = f'estoque_data_{data_posicao}'
        if usar_cache:
            cached_result = cache.get(cache_key)
            if cached_result:
                cached_result['cache_hit'] = True
                return Response(cached_result)
        
        # 3. Query otimizada usando SQL direto
        with connection.cursor() as cursor:
            sql = """
            SELECT 
                me.produto_id,
                p.codigo,
                p.nome,
                COALESCE(p.preco_custo, 0) as custo_unitario,
                SUM(CASE 
                    WHEN tme.tipo = 'E' THEN me.quantidade 
                    WHEN tme.tipo = 'S' THEN -me.quantidade 
                    ELSE 0 
                END) as saldo_final
            FROM movimentacoes_estoque me
            INNER JOIN produtos p ON me.produto_id = p.id
            INNER JOIN tipos_movimentacao_estoque tme ON me.tipo_movimentacao_id = tme.id
            WHERE DATE(me.data_movimentacao) <= %s
            GROUP BY me.produto_id, p.codigo, p.nome, p.preco_custo
            HAVING SUM(CASE 
                WHEN tme.tipo = 'E' THEN me.quantidade 
                WHEN tme.tipo = 'S' THEN -me.quantidade 
                ELSE 0 
            END) > 0
            ORDER BY saldo_final DESC
            """
            
            cursor.execute(sql, [data_posicao])
            resultados = cursor.fetchall()
        
        # 4. Processar resultados
        valor_total_estoque = Decimal('0.00')
        detalhes_produtos = []
        
        for produto_id, codigo, nome, custo, saldo in resultados:
            custo_decimal = Decimal(str(custo))
            saldo_decimal = Decimal(str(saldo))
            valor_produto = saldo_decimal * custo_decimal
            valor_total_estoque += valor_produto
            
            detalhes_produtos.append({
                'produto_id': produto_id,
                'produto_codigo': codigo,
                'produto_descricao': nome,
                'quantidade_em_estoque': saldo_decimal,
                'custo_unitario': custo_decimal,
                'valor_total_produto': valor_produto
            })
        
        # 5. Resposta
        response_data = {
            'data_posicao': data_posicao,
            'valor_total_estoque': valor_total_estoque,
            'total_produtos_em_estoque': len(detalhes_produtos),
            'detalhes_por_produto': detalhes_produtos,
            'cache_hit': False,
            'otimizado': True
        }
        
        # 6. Salvar no cache (1 hora para dados do dia, 24h para dados antigos)
        if usar_cache:
            timeout = 3600 if data_posicao == date.today() else 86400
            cache.set(cache_key, response_data, timeout)
        
        return Response(response_data)
        
    except Exception as e:
        return Response(
            {'error': f'Erro interno: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def refresh_cache_estoque(request):
    """
    Endpoint para limpar cache de estoque
    """
    try:
        data_str = request.data.get('data')
        if data_str:
            cache_key = f'estoque_data_{data_str}'
            cache.delete(cache_key)
            return Response({'message': f'Cache removido para {data_str}'})
        else:
            # Remove todos os caches de estoque
            cache.delete_many(cache.keys('estoque_data_*'))
            return Response({'message': 'Todos os caches de estoque removidos'})
            
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
def estoque_view_materializada(request):
    """
    Endpoint usando view materializada (muito rápido)
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    produto_id,
                    produto_codigo,
                    produto_nome,
                    saldo_atual,
                    custo_unitario,
                    saldo_atual * COALESCE(custo_unitario, 0) as valor_total,
                    ultima_movimentacao
                FROM view_saldos_estoque_rapido
                ORDER BY saldo_atual DESC
            """)
            
            colunas = [desc[0] for desc in cursor.description]
            resultados = [dict(zip(colunas, row)) for row in cursor.fetchall()]
        
        valor_total = sum(r['valor_total'] or 0 for r in resultados)
        
        return Response({
            'produtos': resultados,
            'total_produtos': len(resultados),
            'valor_total': valor_total,
            'fonte': 'view_materializada',
            'observacao': 'Dados podem estar até 1 hora desatualizados'
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
