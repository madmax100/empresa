from decimal import Decimal
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Dict, Any, List
from django.db.models import (
    Sum, Avg, Count, F, Q, Case, When, DecimalField, 
    ExpressionWrapper, FloatField
)
from django.db.models.expressions import Value
from django.db.models.functions import Coalesce, Cast
from rest_framework.decorators import action
from rest_framework.response import Response

class VendasEstoqueMixin:
    """
    Mixin para análise integrada de vendas e estoque com fluxo de caixa
    """

    @action(detail=False, methods=['GET'])
    def dashboard_comercial(self, request):
        """
        Dashboard com análise comercial integrada
        - Vendas vs Locações
        - Desempenho por produto
        - Análise de estoque
        - Indicadores comerciais
        """
        try:
            # Parâmetros
            data_inicial = datetime.strptime(
                request.query_params.get('data_inicial', 
                    (date.today() - timedelta(days=30)).strftime('%Y-%m-%d')),
                '%Y-%m-%d'
            ).date()
            data_final = datetime.strptime(
                request.query_params.get('data_final', 
                    date.today().strftime('%Y-%m-%d')),
                '%Y-%m-%d'
            ).date()

            # Análises
            vendas = self._analisar_vendas(data_inicial, data_final)
            locacoes = self._analisar_locacoes(data_inicial, data_final)
            estoque = self._analisar_estoque(data_inicial, data_final)
            indicadores = self._calcular_indicadores_comerciais(
                vendas, locacoes, estoque
            )

            return Response({
                'periodo': {
                    'inicio': data_inicial,
                    'fim': data_final
                },
                'vendas': vendas,
                'locacoes': locacoes,
                'estoque': estoque,
                'indicadores': indicadores,
                'recomendacoes': self._gerar_recomendacoes_comerciais(
                    vendas, locacoes, estoque, indicadores
                )
            })

        except Exception as e:
            return Response({'error': str(e)}, status=400)

    def _analisar_vendas(self, data_inicial: date, data_final: date) -> Dict[str, Any]:
        """Análise detalhada das vendas"""
        from contas.models import ItensNfSaida, NotasFiscaisSaida

        vendas = ItensNfSaida.objects.filter(
            nota_fiscal__data__range=[data_inicial, data_final],
            nota_fiscal__tipo='V'  # Vendas
        ).select_related('produto', 'nota_fiscal')

        # Totalizadores
        totais = vendas.aggregate(
            quantidade_total=Sum('quantidade'),
            valor_total=Sum('valor_total'),
            custo_total=Sum(F('quantidade') * F('produto__preco_custo')),
            quantidade_itens=Count('id'),
            quantidade_produtos=Count('produto', distinct=True)
        )

        # Análise por produto
        produtos = vendas.values(
            'produto__codigo',
            'produto__nome',
            'produto__categoria__nome'
        ).annotate(
            quantidade_vendida=Sum('quantidade'),
            valor_total=Sum('valor_total'),
            custo_total=Sum(F('quantidade') * F('produto__preco_custo')),
            ticket_medio=Avg('valor_unitario'),
            margem=ExpressionWrapper(
                (F('valor_total') - Sum(F('quantidade') * F('produto__preco_custo'))) /
                F('valor_total') * 100,
                output_field=FloatField()
            )
        ).order_by('-valor_total')

        # Análise temporal
        vendas_diarias = vendas.values(
            'nota_fiscal__data'
        ).annotate(
            quantidade=Sum('quantidade'),
            valor_total=Sum('valor_total'),
            quantidade_notas=Count('nota_fiscal', distinct=True)
        ).order_by('nota_fiscal__data')

        return {
            'totalizadores': {
                'quantidade': totais['quantidade_total'],
                'valor_total': float(totais['valor_total'] or 0),
                'custo_total': float(totais['custo_total'] or 0),
                'margem_total': float(
                    ((totais['valor_total'] or 0) - (totais['custo_total'] or 0)) /
                    (totais['valor_total'] or 1) * 100
                ),
                'quantidade_itens': totais['quantidade_itens'],
                'quantidade_produtos': totais['quantidade_produtos']
            },
            'produtos': [{
                'codigo': p['produto__codigo'],
                'nome': p['produto__nome'],
                'categoria': p['produto__categoria__nome'],
                'quantidade': p['quantidade_vendida'],
                'valor_total': float(p['valor_total']),
                'ticket_medio': float(p['ticket_medio']),
                'margem': float(p['margem'])
            } for p in produtos],
            'evolucao_diaria': [{
                'data': v['nota_fiscal__data'],
                'quantidade': v['quantidade'],
                'valor_total': float(v['valor_total']),
                'quantidade_notas': v['quantidade_notas']
            } for v in vendas_diarias]
        }

    def _analisar_locacoes(self, data_inicial: date, data_final: date) -> Dict[str, Any]:
        """Análise detalhada das locações"""
        from contas.models import ContratosLocacao, ItensContratoLocacao

        contratos = ContratosLocacao.objects.filter(
            Q(inicio__range=[data_inicial, data_final]) |
            Q(fim__range=[data_inicial, data_final]) |
            Q(inicio__lte=data_inicial, fim__gte=data_final)
        ).select_related('cliente')

        # Totalizadores
        totais = contratos.aggregate(
            valor_total=Sum('valorcontrato'),
            quantidade_contratos=Count('id')
        )

        # Análise por produto
        itens = ItensContratoLocacao.objects.filter(
            contrato__in=contratos
        ).values(
            'produto__codigo',
            'produto__nome',
            'produto__categoria__nome'
        ).annotate(
            quantidade=Count('id'),
            valor_total=Sum('valor_locacao'),
            valor_medio=Avg('valor_locacao')
        ).order_by('-quantidade')

        return {
            'totalizadores': {
                'valor_total': float(totais['valor_total'] or 0),
                'quantidade_contratos': totais['quantidade_contratos'],
                'ticket_medio': float(
                    (totais['valor_total'] or 0) / totais['quantidade_contratos']
                    if totais['quantidade_contratos'] > 0 else 0
                )
            },
            'produtos': [{
                'codigo': i['produto__codigo'],
                'nome': i['produto__nome'],
                'categoria': i['produto__categoria__nome'],
                'quantidade': i['quantidade'],
                'valor_total': float(i['valor_total']),
                'valor_medio': float(i['valor_medio'])
            } for i in itens],
            'status': self._analisar_status_contratos(contratos)
        }

    def _analisar_status_contratos(self, contratos) -> Dict[str, Any]:
        """Análise dos status dos contratos"""
        return contratos.values(
            'status'
        ).annotate(
            quantidade=Count('id'),
            valor_total=Sum('valorcontrato')
        ).order_by('status')

    def _analisar_estoque(self, data_inicial: date, data_final: date) -> Dict[str, Any]:
        """Análise detalhada do estoque"""
        from contas.models import MovimentacoesEstoque, SaldosEstoque, Produtos

        # Movimentações do período
        movimentacoes = MovimentacoesEstoque.objects.filter(
            data_movimentacao__range=[data_inicial, data_final]
        ).select_related('produto', 'tipo_movimentacao')

        # Análise por tipo de movimento
        mov_por_tipo = movimentacoes.values(
            'tipo_movimentacao__tipo',
            'tipo_movimentacao__descricao'
        ).annotate(
            quantidade=Sum('quantidade'),
            valor_total=Sum(F('quantidade') * F('custo_unitario'))
        )

        # Análise por produto
        produtos = Produtos.objects.filter(
            disponivel_locacao=True
        ).annotate(
            entradas=Sum(Case(
                When(movimentacoes_estoque__tipo_movimentacao__tipo='E',
                     movimentacoes_estoque__data_movimentacao__range=[data_inicial, data_final],
                     then='movimentacoes_estoque__quantidade'),
                default=0
            )),
            saidas=Sum(Case(
                When(movimentacoes_estoque__tipo_movimentacao__tipo='S',
                     movimentacoes_estoque__data_movimentacao__range=[data_inicial, data_final],
                     then='movimentacoes_estoque__quantidade'),
                default=0
            ))
        )

        # Saldos atuais
        saldos = SaldosEstoque.objects.filter(
            produto__disponivel_locacao=True
        ).select_related('produto')

        return {
            'movimentacoes': {
                'por_tipo': [{
                    'tipo': m['tipo_movimentacao__tipo'],
                    'descricao': m['tipo_movimentacao__descricao'],
                    'quantidade': m['quantidade'],
                    'valor_total': float(m['valor_total'])
                } for m in mov_por_tipo],
                'quantidade_total': movimentacoes.count()
            },
            'produtos': [{
                'codigo': p.codigo,
                'nome': p.nome,
                'categoria': p.categoria.nome if p.categoria else None,
                'entradas': p.entradas or 0,
                'saidas': p.saidas or 0,
                'saldo': p.saldos_estoque.first().quantidade
                if p.saldos_estoque.exists() else 0
            } for p in produtos],
            'alertas': self._gerar_alertas_estoque(saldos)
        }

    def _gerar_alertas_estoque(self, saldos) -> List[Dict[str, Any]]:
        """Gera alertas de estoque"""
        alertas = []

        for saldo in saldos:
            # Estoque baixo
            if saldo.quantidade <= saldo.produto.estoque_minimo:
                alertas.append({
                    'tipo': 'estoque_baixo',
                    'severidade': 'alta',
                    'produto': {
                        'codigo': saldo.produto.codigo,
                        'nome': saldo.produto.nome
                    },
                    'saldo_atual': saldo.quantidade,
                    'minimo': saldo.produto.estoque_minimo
                })

            # Estoque parado
            ultima_movimentacao = saldo.produto.movimentacoes_estoque.order_by(
                '-data_movimentacao'
            ).first()

            if ultima_movimentacao:
                dias_parado = (date.today() - ultima_movimentacao.data_movimentacao).days
                if dias_parado > 90:  # Mais de 90 dias sem movimentação
                    alertas.append({
                        'tipo': 'estoque_parado',
                        'severidade': 'media',
                        'produto': {
                            'codigo': saldo.produto.codigo,
                            'nome': saldo.produto.nome
                        },
                        'dias_parado': dias_parado,
                        'valor_parado': float(
                            saldo.quantidade * saldo.produto.preco_custo
                        )
                    })

        return alertas

    def _calcular_indicadores_comerciais(self, vendas, locacoes, estoque) -> Dict[str, Any]:
        """Calcula indicadores comerciais integrados"""
        receita_total = (
            vendas['totalizadores']['valor_total'] +
            locacoes['totalizadores']['valor_total']
        )

        return {
            'mix_receita': {
                'vendas': float(
                    vendas['totalizadores']['valor_total'] / receita_total * 100
                    if receita_total > 0 else 0
                ),
                'locacoes': float(
                    locacoes['totalizadores']['valor_total'] / receita_total * 100
                    if receita_total > 0 else 0
                )
            },
            'margens': {
                'vendas': float(
                    vendas['totalizadores']['margem_total']
                ),
                'geral': float(
                    vendas['totalizadores']['margem_total'] * 
                    (vendas['totalizadores']['valor_total'] / receita_total)
                    if receita_total > 0 else 0
                )
            },
            'giro_estoque': self._calcular_giro_estoque(vendas, estoque),
            'conversao': {
                'leads_contratos': float(
                    locacoes['totalizadores']['quantidade_contratos'] /
                    # Aqui você precisaria ter a quantidade de leads
                    # Por enquanto vamos usar um valor fictício
                    100 * 100  # Multiplica por 100 para ter percentual
                )
            }
        }

    def _calcular_giro_estoque(self, vendas, estoque) -> float:
        """Calcula o giro de estoque"""
        custo_vendas = vendas['totalizadores']['custo_total']
        
        # Calcula estoque médio
        estoque_total = sum(
            p['saldo'] * p.get('custo', 0)  # Você precisaria ter o custo aqui
            for p in estoque['produtos']
        )
        
        if estoque_total > 0:
            return float(custo_vendas / estoque_total)
        return 0.0

    def _gerar_recomendacoes_comerciais(self, vendas, locacoes, 
                                      estoque, indicadores) -> List[Dict[str, str]]:
        """Gera recomendações comerciais baseadas nas análises"""
        recomendacoes = []

        # Análise de mix de receita
        if indicadores['mix_receita']['vendas'] < 30:
            recomendacoes.append({
                'tipo': 'mix_receita',
                'severidade': 'media', 'mensagem': 'Baixa participação de vendas na receita',
                'acoes': [
                    'Revisar política comercial de vendas',
                    'Identificar oportunidades de venda de equipamentos',
                    'Desenvolver campanhas específicas para vendas'
                ]
            })

        # Análise de margens
        if indicadores['margens']['vendas'] < 25:
            recomendacoes.append({
                'tipo': 'margem',
                'severidade': 'alta',
                'mensagem': 'Margem de vendas abaixo do esperado',
                'acoes': [
                    'Revisar política de preços',
                    'Analisar custos de aquisição',
                    'Identificar produtos com melhor rentabilidade'
                ]
            })

        # Análise de estoque
        produtos_parados = [p for p in estoque['produtos'] if p.get('dias_parado', 0) > 90]
        if produtos_parados:
            recomendacoes.append({
                'tipo': 'estoque',
                'severidade': 'media',
                'mensagem': f'{len(produtos_parados)} produtos com estoque parado',
                'acoes': [
                    'Realizar campanha para produtos parados',
                    'Avaliar transferência entre filiais',
                    'Considerar baixa de estoque obsoleto'
                ]
            })

        # Análise de conversão
        if indicadores['conversao']['leads_contratos'] < 20:
            recomendacoes.append({
                'tipo': 'conversao',
                'severidade': 'alta',
                'mensagem': 'Baixa taxa de conversão de leads',
                'acoes': [
                    'Revisar processo comercial',
                    'Treinar equipe de vendas',
                    'Melhorar qualificação de leads'
                ]
            })

        return recomendacoes

    @action(detail=False, methods=['GET'])
    def analise_rentabilidade(self, request):
        """
        Análise detalhada de rentabilidade
        - Por produto
        - Por categoria
        - Por tipo de operação
        """
        try:
            # Parâmetros
            data_inicial = datetime.strptime(
                request.query_params.get('data_inicial', 
                    (date.today() - timedelta(days=30)).strftime('%Y-%m-%d')),
                '%Y-%m-%d'
            ).date()
            data_final = datetime.strptime(
                request.query_params.get('data_final', 
                    date.today().strftime('%Y-%m-%d')),
                '%Y-%m-%d'
            ).date()

            # Análises
            rentabilidade = self._analisar_rentabilidade(data_inicial, data_final)
            evolucao = self._analisar_evolucao_rentabilidade(data_inicial, data_final)
            comparativos = self._gerar_comparativos_rentabilidade(rentabilidade)

            return Response({
                'periodo': {
                    'inicio': data_inicial,
                    'fim': data_final
                },
                'rentabilidade': rentabilidade,
                'evolucao': evolucao,
                'comparativos': comparativos,
                'recomendacoes': self._gerar_recomendacoes_rentabilidade(
                    rentabilidade, evolucao
                )
            })

        except Exception as e:
            return Response({'error': str(e)}, status=400)

    def _analisar_rentabilidade(self, data_inicial: date, data_final: date) -> Dict[str, Any]:
        """Análise detalhada de rentabilidade"""
        from contas.models import ItensNfSaida, ItensContratoLocacao

        # Rentabilidade de vendas
        vendas = ItensNfSaida.objects.filter(
            nota_fiscal__data__range=[data_inicial, data_final]
        ).values(
            'produto__codigo',
            'produto__nome',
            'produto__categoria__nome'
        ).annotate(
            quantidade=Sum('quantidade'),
            receita=Sum('valor_total'),
            custo=Sum(F('quantidade') * F('produto__preco_custo')),
            margem=ExpressionWrapper(
                (F('valor_total') - Sum(F('quantidade') * F('produto__preco_custo'))) /
                F('valor_total') * 100,
                output_field=FloatField()
            )
        ).order_by('-margem')

        # Rentabilidade de locações
        locacoes = ItensContratoLocacao.objects.filter(
            Q(contrato__inicio__range=[data_inicial, data_final]) |
            Q(contrato__fim__range=[data_inicial, data_final])
        ).values(
            'produto__codigo',
            'produto__nome',
            'produto__categoria__nome'
        ).annotate(
            quantidade=Count('id'),
            receita=Sum('valor_locacao'),
            custo=Sum(F('produto__preco_custo')),
            margem=ExpressionWrapper(
                (F('valor_locacao') - F('produto__preco_custo')) /
                F('valor_locacao') * 100,
                output_field=FloatField()
            )
        ).order_by('-margem')

        return {
            'vendas': [{
                'produto': {
                    'codigo': v['produto__codigo'],
                    'nome': v['produto__nome'],
                    'categoria': v['produto__categoria__nome']
                },
                'quantidade': v['quantidade'],
                'receita': float(v['receita']),
                'custo': float(v['custo']),
                'margem': float(v['margem'])
            } for v in vendas],
            'locacoes': [{
                'produto': {
                    'codigo': l['produto__codigo'],
                    'nome': l['produto__nome'],
                    'categoria': l['produto__categoria__nome']
                },
                'quantidade': l['quantidade'],
                'receita': float(l['receita']),
                'custo': float(l['custo']),
                'margem': float(l['margem'])
            } for l in locacoes]
        }

    def _analisar_evolucao_rentabilidade(self, data_inicial: date, 
                                        data_final: date) -> List[Dict[str, Any]]:
        """Análise da evolução da rentabilidade no período"""
        from contas.models import ItensNfSaida, ItensContratoLocacao

        # Define períodos de análise (mensal)
        periodos = []
        data_atual = data_inicial
        while data_atual <= data_final:
            proximo_mes = (data_atual + relativedelta(months=1)).replace(day=1)
            fim_periodo = min(proximo_mes - timedelta(days=1), data_final)
            
            periodos.append({
                'inicio': data_atual,
                'fim': fim_periodo
            })
            data_atual = proximo_mes

        # Analisa cada período
        evolucao = []
        for periodo in periodos:
            # Rentabilidade vendas
            vendas = ItensNfSaida.objects.filter(
                nota_fiscal__data__range=[periodo['inicio'], periodo['fim']]
            ).aggregate(
                receita=Sum('valor_total'),
                custo=Sum(F('quantidade') * F('produto__preco_custo'))
            )

            # Rentabilidade locações
            locacoes = ItensContratoLocacao.objects.filter(
                Q(contrato__inicio__range=[periodo['inicio'], periodo['fim']]) |
                Q(contrato__fim__range=[periodo['inicio'], periodo['fim']])
            ).aggregate(
                receita=Sum('valor_locacao'),
                custo=Sum('produto__preco_custo')
            )

            receita_total = (vendas['receita'] or 0) + (locacoes['receita'] or 0)
            custo_total = (vendas['custo'] or 0) + (locacoes['custo'] or 0)

            evolucao.append({
                'periodo': {
                    'inicio': periodo['inicio'],
                    'fim': periodo['fim']
                },
                'receita_total': float(receita_total),
                'custo_total': float(custo_total),
                'margem': float(
                    ((receita_total - custo_total) / receita_total * 100)
                    if receita_total > 0 else 0
                ),
                'detalhamento': {
                    'vendas': {
                        'receita': float(vendas['receita'] or 0),
                        'custo': float(vendas['custo'] or 0),
                        'margem': float(
                            ((vendas['receita'] or 0) - (vendas['custo'] or 0)) /
                            (vendas['receita'] or 1) * 100
                        )
                    },
                    'locacoes': {
                        'receita': float(locacoes['receita'] or 0),
                        'custo': float(locacoes['custo'] or 0),
                        'margem': float(
                            ((locacoes['receita'] or 0) - (locacoes['custo'] or 0)) /
                            (locacoes['receita'] or 1) * 100
                        )
                    }
                }
            })

        return evolucao

    def _gerar_comparativos_rentabilidade(self, rentabilidade: Dict[str, Any]) -> Dict[str, Any]:
        """Gera comparativos de rentabilidade"""
        return {
            'margem_media': {
                'vendas': float(
                    sum(v['margem'] for v in rentabilidade['vendas']) /
                    len(rentabilidade['vendas']) if rentabilidade['vendas'] else 0
                ),
                'locacoes': float(
                    sum(l['margem'] for l in rentabilidade['locacoes']) /
                    len(rentabilidade['locacoes']) if rentabilidade['locacoes'] else 0
                )
            },
            'melhores_produtos': {
                'vendas': sorted(
                    rentabilidade['vendas'],
                    key=lambda x: x['margem'],
                    reverse=True
                )[:5],
                'locacoes': sorted(
                    rentabilidade['locacoes'],
                    key=lambda x: x['margem'],
                    reverse=True
                )[:5]
            },
            'piores_produtos': {
                'vendas': sorted(
                    rentabilidade['vendas'],
                    key=lambda x: x['margem']
                )[:5],
                'locacoes': sorted(
                    rentabilidade['locacoes'],
                    key=lambda x: x['margem']
                )[:5]
            }
        }

    def _gerar_recomendacoes_rentabilidade(self, rentabilidade: Dict[str, Any], 
                                          evolucao: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Gera recomendações baseadas na análise de rentabilidade"""
        recomendacoes = []

        # Analisa tendência de margem
        if len(evolucao) >= 2:
            margem_atual = evolucao[-1]['margem']
            margem_anterior = evolucao[-2]['margem']
            
            if margem_atual < margem_anterior:
                recomendacoes.append({
                    'tipo': 'tendencia_margem',
                    'severidade': 'alta',
                    'mensagem': 'Tendência de queda na margem',
                    'acoes': [
                        'Revisar estrutura de custos',
                        'Analisar política de preços',
                        'Identificar produtos com melhor rentabilidade'
                    ]
                })

        # Analisa produtos com margem negativa
        produtos_negativos_venda = [
            p for p in rentabilidade['vendas']
            if p['margem'] < 0
        ]
        
        if produtos_negativos_venda:
            recomendacoes.append({
                'tipo': 'margem_negativa',
                'severidade': 'alta',
                'mensagem': f'{len(produtos_negativos_venda)} produtos com margem negativa em vendas',
                'acoes': [
                    'Reavaliar preços destes produtos',
                    'Analisar custos de aquisição',
                    'Considerar descontinuar produtos'
                ]
            })

        # Analisa dispersão de margens
        margens_vendas = [p['margem'] for p in rentabilidade['vendas']]
        if margens_vendas:
            desvio = self._calcular_desvio_padrao(margens_vendas)
            if desvio > 20:  # Alto desvio nas margens
                recomendacoes.append({
                    'tipo': 'dispersao_margens',
                    'severidade': 'media',
                    'mensagem': 'Alta variação nas margens entre produtos',
                    'acoes': [
                        'Padronizar política de preços',
                        'Revisar custos por categoria',
                        'Estabelecer margens mínimas por linha'
                    ]
                })

        return recomendacoes

    def _calcular_desvio_padrao(self, valores: List[float]) -> float:
        """Calcula o desvio padrão de uma lista de valores"""
        if not valores:
            return 0
            
        media = sum(valores) / len(valores)
        soma_quadrados = sum((x - media) ** 2 for x in valores)
        return (soma_quadrados / len(valores)) ** 0.5