from decimal import Decimal
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Dict, Any, List
from django.db.models import Sum, Avg, Count, F, Q, Case, When, DecimalField, Max
from django.db.models.functions import TruncMonth
from rest_framework.decorators import action
from rest_framework.response import Response

class ClienteAnalysisMixin:
    """
    Mixin para análises detalhadas por cliente
    """
    
    @action(detail=False, methods=['GET'])
    def analise_cliente(self, request):
        """Análise completa de um cliente específico"""
        try:
            cliente_id = request.query_params.get('cliente_id')
            if not cliente_id:
                return Response({'error': 'Cliente não especificado'}, status=400)

            periodo_meses = int(request.query_params.get('periodo_meses', 12))
            data_final = date.today()
            data_inicial = data_final - relativedelta(months=periodo_meses)

            # Filtra lançamentos do cliente
            lancamentos = self.get_queryset().filter(
                cliente_id=cliente_id,
                data__range=[data_inicial, data_final]
            )

            # Análises
            metricas = self._calcular_metricas_cliente(lancamentos)
            historico = self._analisar_historico_cliente(lancamentos)
            comportamento = self._analisar_comportamento_pagamento(lancamentos)
            categorias = self._analisar_categorias_cliente(lancamentos)
            tendencias = self._analisar_tendencias_cliente(lancamentos)

            return Response({
                'cliente_id': cliente_id,
                'periodo': {
                    'inicio': data_inicial,
                    'fim': data_final,
                    'meses': periodo_meses
                },
                'metricas': metricas,
                'historico': historico,
                'comportamento_pagamento': comportamento,
                'analise_categorias': categorias,
                'tendencias': tendencias,
                'recomendacoes': self._gerar_recomendacoes_cliente(
                    metricas, historico, comportamento, categorias, tendencias
                )
            })

        except Exception as e:
            return Response({'error': str(e)}, status=400)

    def _calcular_metricas_cliente(self, lancamentos) -> Dict[str, Any]:
        """Calcula métricas principais do cliente"""
        # Totais gerais
        totais = lancamentos.aggregate(
            total_entradas=Sum(Case(
                When(tipo='entrada', then='valor'),
                default=0,
                output_field=DecimalField()
            )),
            total_saidas=Sum(Case(
                When(tipo='saida', then='valor'),
                default=0,
                output_field=DecimalField()
            )),
            quantidade_lancamentos=Count('id'),
            ticket_medio=Avg(Case(
                When(tipo='entrada', then='valor'),
                default=None,
                output_field=DecimalField()
            ))
        )

        # Totais realizados vs previstos
        realizados = lancamentos.filter(realizado=True).aggregate(
            total=Sum(Case(
                When(tipo='entrada', then='valor'),
                When(tipo='saida', then=F('valor') * -1),
                output_field=DecimalField()
            ))
        )['total'] or Decimal('0')

        previstos = lancamentos.filter(realizado=False).aggregate(
            total=Sum(Case(
                When(tipo='entrada', then='valor'),
                When(tipo='saida', then=F('valor') * -1),
                output_field=DecimalField()
            ))
        )['total'] or Decimal('0')

        return {
            'faturamento_total': float(totais['total_entradas'] or 0),
            'despesas_total': float(totais['total_saidas'] or 0),
            'resultado_liquido': float((totais['total_entradas'] or 0) - (totais['total_saidas'] or 0)),
            'quantidade_lancamentos': totais['quantidade_lancamentos'],
            'ticket_medio': float(totais['ticket_medio'] or 0),
            'realizados': float(realizados),
            'previstos': float(previstos),
            'percentual_realizado': float(
                (realizados / (realizados + previstos) * 100)
                if (realizados + previstos) > 0 else 0
            )
        }

    def _analisar_historico_cliente(self, lancamentos) -> Dict[str, Any]:
        """Analisa histórico de transações do cliente"""
        # Agrupa por mês
        historico_mensal = (
            lancamentos.annotate(mes=TruncMonth('data'))
            .values('mes')
            .annotate(
                entradas=Sum(Case(
                    When(tipo='entrada', then='valor'),
                    default=0,
                    output_field=DecimalField()
                )),
                saidas=Sum(Case(
                    When(tipo='saida', then='valor'),
                    default=0,
                    output_field=DecimalField()
                )),
                quantidade=Count('id')
            )
            .order_by('mes')
        )

        # Calcula variações
        historico_processado = []
        for i, mes in enumerate(historico_mensal):
            variacao = 0
            if i > 0:
                mes_anterior = historico_mensal[i-1]['entradas']
                if mes_anterior > 0:
                    variacao = ((mes['entradas'] - mes_anterior) / mes_anterior) * 100

            historico_processado.append({
                'mes': mes['mes'],
                'entradas': float(mes['entradas']),
                'saidas': float(mes['saidas']),
                'quantidade': mes['quantidade'],
                'variacao_percentual': float(variacao)
            })

        return {
            'historico_mensal': historico_processado,
            'media_mensal': float(
                sum(m['entradas'] for m in historico_processado) / 
                len(historico_processado) if historico_processado else 0
            ),
            'meses_crescimento': len([
                m for m in historico_processado 
                if m['variacao_percentual'] > 0
            ]),
            'maior_faturamento': max(
                (m['entradas'] for m in historico_processado),
                default=0
            )
        }

    def _analisar_comportamento_pagamento(self, lancamentos) -> Dict[str, Any]:
        """Analisa comportamento de pagamento do cliente"""
        lancamentos_realizados = lancamentos.filter(realizado=True)
        
        # Atrasos
        atrasos = lancamentos_realizados.filter(
            data_realizacao__gt=F('data')
        ).annotate(
            dias_atraso=(F('data_realizacao__date') - F('data'))
        ).aggregate(
            total_atrasos=Count('id'),
            media_dias_atraso=Avg('dias_atraso'),
            maior_atraso=Max('dias_atraso')
        )

        # Pagamentos em dia
        pagamentos_dia = lancamentos_realizados.filter(
            data_realizacao__date=F('data')
        ).count()

        total_pagamentos = lancamentos_realizados.count()

        return {
            'total_pagamentos': total_pagamentos,
            'pagamentos_em_dia': pagamentos_dia,
            'total_atrasos': atrasos['total_atrasos'],
            'media_dias_atraso': float(atrasos['media_dias_atraso'] or 0),
            'maior_atraso': atrasos['maior_atraso'],
            'pontualidade': float(
                (pagamentos_dia / total_pagamentos * 100)
                if total_pagamentos > 0 else 0
            )
        }

    def _analisar_categorias_cliente(self, lancamentos) -> Dict[str, Any]:
        """Analisa distribuição por categorias"""
        categorias = lancamentos.values(
            'categoria'
        ).annotate(
            total=Sum('valor'),
            quantidade=Count('id'),
            ticket_medio=Avg('valor')
        ).order_by('-total')

        total_geral = sum(cat['total'] for cat in categorias)

        return [{
            'categoria': cat['categoria'],
            'total': float(cat['total']),
            'quantidade': cat['quantidade'],
            'ticket_medio': float(cat['ticket_medio']),
            'participacao': float(
                (cat['total'] / total_geral * 100)
                if total_geral > 0 else 0
            )
        } for cat in categorias]

    def _analisar_tendencias_cliente(self, lancamentos) -> Dict[str, Any]:
        """Analisa tendências do cliente"""
        # Últimos 3 meses vs 3 meses anteriores
        hoje = date.today()
        ultimos_3_meses = lancamentos.filter(
            data__gte=hoje - relativedelta(months=3)
        )
        meses_anteriores = lancamentos.filter(
            data__range=[
                hoje - relativedelta(months=6),
                hoje - relativedelta(months=3)
            ]
        )

        # Calcula totais
        total_recente = ultimos_3_meses.filter(
            tipo='entrada'
        ).aggregate(
            total=Sum('valor')
        )['total'] or Decimal('0')

        total_anterior = meses_anteriores.filter(
            tipo='entrada'
        ).aggregate(
            total=Sum('valor')
        )['total'] or Decimal('1')  # Evita divisão por zero

        # Crescimento
        crescimento = ((total_recente / total_anterior) - 1) * 100

        return {
            'tendencia_crescimento': float(crescimento),
            'classificacao': self._classificar_tendencia(crescimento),
            'projecao_proximos_meses': float(total_recente * Decimal('1.1')),
            'sazonalidade': self._identificar_sazonalidade(lancamentos)
        }

    def _classificar_tendencia(self, crescimento: Decimal) -> str:
        """Classifica a tendência do cliente"""
        if crescimento > 20:
            return 'forte_crescimento'
        elif crescimento > 5:
            return 'crescimento_moderado'
        elif crescimento > -5:
            return 'estavel'
        elif crescimento > -20:
            return 'declinio_moderado'
        return 'forte_declinio'

    def _identificar_sazonalidade(self, lancamentos) -> Dict[str, List[int]]:
        """Identifica padrões sazonais"""
        meses_pico = []
        meses_baixa = []

        # Analisa por mês
        for mes in range(1, 13):
            lancamentos_mes = lancamentos.filter(data__month=mes)
            media_mes = lancamentos_mes.filter(
                tipo='entrada'
            ).aggregate(
                media=Avg('valor')
            )['media'] or 0

            # Calcula média geral
            media_geral = lancamentos.filter(
                tipo='entrada'
            ).aggregate(
                media=Avg('valor')
            )['media'] or 1

            # Identifica picos e baixas
            if media_mes > (media_geral * Decimal('1.2')):
                meses_pico.append(mes)
            elif media_mes < (media_geral * Decimal('0.8')):
                meses_baixa.append(mes)

        return {
            'meses_pico': meses_pico,
            'meses_baixa': meses_baixa
        }

    def _gerar_recomendacoes_cliente(self, metricas, historico, comportamento,
                                    categorias, tendencias) -> List[Dict[str, str]]:
        """Gera recomendações baseadas nas análises"""
        recomendacoes = []

        # Análise de faturamento
        if metricas['ticket_medio'] < 1000:
            recomendacoes.append({
                'tipo': 'faturamento',
                'severidade': 'media',
                'descricao': 'Ticket médio baixo',
                'acao': 'Avaliar oportunidades de up-selling'
            })

        # Análise de pontualidade
        if comportamento['pontualidade'] < 80:
            recomendacoes.append({
                'tipo': 'pagamento',
                'severidade': 'alta',
                'descricao': 'Baixa pontualidade nos pagamentos',
                'acao': 'Revisar condições de pagamento e crédito'
            })

        # Análise de tendência
        if tendencias['tendencia_crescimento'] < -10:
            recomendacoes.append({
                'tipo': 'relacionamento',
                'severidade': 'alta',
                'descricao': 'Cliente em declínio',
                'acao': 'Agendar reunião de relacionamento'
            })

        # Análise de concentração
        categoria_principal = max(
            categorias,
            key=lambda x: x['participacao']
        ) if categorias else {'participacao': 0}

        if categoria_principal['participacao'] > 80:
            recomendacoes.append({
                'tipo': 'diversificacao',
                'severidade': 'media',
                'descricao': 'Alta concentração em uma categoria',
                'acao': 'Apresentar produtos/serviços de outras categorias'
            })

        return recomendacoes

    @action(detail=False, methods=['GET'])
    def ranking_clientes(self, request):
        """Gera ranking de clientes por diferentes métricas"""
        try:
            periodo_meses = int(request.query_params.get('periodo_meses', 12))
            data_final = date.today()
            data_inicial = data_final - relativedelta(months=periodo_meses)

            lancamentos = self.get_queryset().filter(
                data__range=[data_inicial, data_final]
            )

            # Ranking por faturamento
            ranking_faturamento = (
                lancamentos.filter(tipo='entrada')
                .values('cliente', 'cliente__nome')
                .annotate(
                    total=Sum('valor'),
                    quantidade=Count('id'),
                    ticket_medio=Avg('valor')
                )
                .order_by('-total')
            )

            # Ranking por pontualidade
            ranking_pontualidade = (
                lancamentos.filter(realizado=True)
                .values('cliente', 'cliente__nome')
                .annotate(
                    total_lancamentos=Count('id'),
                    pagamentos_dia=Count(Case(
                        When(data_realizacao__date=F('data'), then=1)
                    )),
                    media_atraso=Avg(Case(
                        When(data_realizacao__date__gt=F('data'),
                             then=F('data_realizacao__date') - F('data')),
                        default=0,
                        output_field=DecimalField()
                    ))
                )
                .order_by('media_atraso')
            )

            # Ranking por crescimento
            ranking_crescimento = []
            for cliente in ranking_faturamento:
                lanc_cliente = lancamentos.filter(cliente=cliente['cliente'])
                crescimento = self._calcular_crescimento_cliente(lanc_cliente)
                ranking_crescimento.append({
                    'cliente': cliente['cliente'],
                    'cliente_nome': cliente['cliente__nome'],
                    'crescimento': crescimento,
                    'faturamento': float(cliente['total'])
                })

            ranking_crescimento.sort(key=lambda x: x['crescimento'], reverse=True)

            return Response({
                'periodo': {
                    'inicio': data_inicial,
                    'fim': data_final,
                    'meses': periodo_meses
                },
                'ranking_faturamento': [{
                    'cliente': c['cliente'],
                    'cliente_nome': c['cliente__nome'],
                    'faturamento': float(c['total']),
                    'quantidade': c['quantidade'],
                    'ticket_medio': float(c['ticket_medio'])
                } for c in ranking_faturamento],
                'ranking_pontualidade': [{
                    'cliente': c['cliente'],
                    'cliente_nome': c['cliente__nome'],
                    'total_lancamentos': c['total_lancamentos'],
                    'pagamentos_dia': c['pagamentos_dia'],
                    'media_atraso': float(c['media_atraso'] or 0),
                    'pontualidade': float(
                        c['pagamentos_dia'] / c['total_lancamentos'] * 100
                    ) if c['total_lancamentos'] > 0 else 0
                } for c in ranking_pontualidade],
                'ranking_crescimento': ranking_crescimento
            })

        except Exception as e:
            return Response({'error': str(e)}, status=400)

    def _calcular_crescimento_cliente(self, lancamentos) -> float:
        """Calcula o percentual de crescimento do cliente"""
        # Divide o período em duas partes
        data_meio = lancamentos.aggregate(
            data_meio=Avg('data')
        )['data_meio']

        if not data_meio:
            return 0

        # Faturamento primeira metade
        faturamento_anterior = lancamentos.filter(
            data__lt=data_meio,
            tipo='entrada'
        ).aggregate(
            total=Sum('valor')
        )['total'] or Decimal('1')  # Evita divisão por zero

        # Faturamento segunda metade
        faturamento_recente = lancamentos.filter(
            data__gte=data_meio,
            tipo='entrada'
        ).aggregate(
            total=Sum('valor')
        )['total'] or Decimal('0')

        return float(((faturamento_recente / faturamento_anterior) - 1) * 100)

    @action(detail=False, methods=['GET'])
    def analise_carteira(self, request):
        """Análise da carteira de clientes"""
        try:
            periodo_meses = int(request.query_params.get('periodo_meses', 12))
            data_final = date.today()
            data_inicial = data_final - relativedelta(months=periodo_meses)

            lancamentos = self.get_queryset().filter(
                data__range=[data_inicial, data_final]
            )

            # Agrupa clientes por faixas de faturamento
            faturamento_clientes = (
                lancamentos.filter(tipo='entrada')
                .values('cliente', 'cliente__nome')
                .annotate(total=Sum('valor'))
            )

            # Define faixas de faturamento
            faixas = {
                'A': Decimal('100000'),  # > 100k
                'B': Decimal('50000'),   # 50k-100k
                'C': Decimal('10000'),   # 10k-50k
                'D': Decimal('0')        # < 10k
            }

            # Classifica clientes
            classificacao = {
                'A': [], 'B': [], 'C': [], 'D': []
            }

            for cliente in faturamento_clientes:
                faturamento = cliente['total']
                for faixa, valor in faixas.items():
                    if faturamento > valor:
                        classificacao[faixa].append({
                            'cliente': cliente['cliente'],
                            'cliente_nome': cliente['cliente__nome'],
                            'faturamento': float(faturamento)
                        })
                        break

            # Análise por faixa
            analise_faixas = {}
            for faixa, clientes in classificacao.items():
                total_faixa = sum(c['faturamento'] for c in clientes)
                analise_faixas[faixa] = {
                    'quantidade_clientes': len(clientes),
                    'faturamento_total': float(total_faixa),
                    'ticket_medio': float(
                        total_faixa / len(clientes) if clientes else 0
                    ),
                    'participacao_carteira': float(
                        total_faixa / sum(
                            sum(c['faturamento'] for c in f)
                            for f in classificacao.values()
                        ) * 100
                    ) if clientes else 0
                }

            return Response({
                'periodo': {
                    'inicio': data_inicial,
                    'fim': data_final,
                    'meses': periodo_meses
                },
                'classificacao': classificacao,
                'analise_faixas': analise_faixas,
                'recomendacoes': self._gerar_recomendacoes_carteira(
                    classificacao,
                    analise_faixas
                )
            })

        except Exception as e:
            return Response({'error': str(e)}, status=400)

    def _gerar_recomendacoes_carteira(self, classificacao, analise_faixas) -> List[Dict[str, str]]:
        """Gera recomendações para gestão da carteira"""
        recomendacoes = []

        # Analisa concentração
        clientes_a = len(classificacao['A'])
        total_clientes = sum(len(c) for c in classificacao.values())

        if clientes_a > 0:
            participacao_a = analise_faixas['A']['participacao_carteira']
            if participacao_a > 60:
                recomendacoes.append({
                    'tipo': 'concentracao',
                    'severidade': 'alta',
                    'descricao': f'Alta concentração em clientes A ({participacao_a:.1f}%)',
                    'acao': 'Desenvolver estratégias para diversificar a carteira'
                })

        # Analisa distribuição
        if total_clientes > 0:
            if len(classificacao['D']) / total_clientes > 0.5:
                recomendacoes.append({
                    'tipo': 'desenvolvimento',
                    'severidade': 'media',
                    'descricao': 'Alto percentual de clientes na faixa D',
                    'acao': 'Desenvolver ações para evolução dos clientes'
                })

        # Analisa potencial
        if len(classificacao['B']) > len(classificacao['A']):
            recomendacoes.append({
                'tipo': 'oportunidade',
                'severidade': 'baixa',
                'descricao': 'Potencial de evolução de clientes B para A',
                'acao': 'Criar plano de desenvolvimento para clientes B'
            })

        return recomendacoes