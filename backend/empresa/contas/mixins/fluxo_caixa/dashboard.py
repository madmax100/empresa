from decimal import Decimal
from datetime import date, datetime, timedelta
import logging
import traceback
from dateutil.relativedelta import relativedelta
from typing import Dict, Any, List
from django.db.models import Sum, Avg, Count, F, Q, Case, When, DecimalField, Value, BooleanField
from django.db.models.functions import TruncDate, TruncMonth
from rest_framework.decorators import action
from rest_framework.response import Response

from contas.models.access import ContratosLocacao
from contas.models.fluxo_caixa import FluxoCaixaLancamento
from contas.services.fluxo_caixa_service import FluxoCaixaService
# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

class DashboardMixin:
    """
    Mixin para dashboards operacionais e gerenciais
    """
    def verificar_categorias(self):
        try:
            # Ver quais categorias existem nos lançamentos
            categorias_existentes = FluxoCaixaLancamento.objects.values('categoria').distinct()
            logger.info("Categorias encontradas nos lançamentos:")
            for cat in categorias_existentes:
                logger.info(f"- {cat['categoria']}")
                
                # Contar quantidade e somar valores por categoria
                total = FluxoCaixaLancamento.objects.filter(
                    categoria=cat['categoria'],
                    tipo='entrada',
                    realizado=True
                ).aggregate(
                    quantidade=Count('id'),
                    valor_total=Sum('valor')
                )
                logger.info(f"  Quantidade: {total['quantidade']}")
                logger.info(f"  Valor Total: {total['valor_total']}")
                
        except Exception as e:
            logger.error(f"Erro ao verificar categorias: {str(e)}")

    @action(detail=False, methods=['GET'])
    def dashboard_operacional(self, request):
        """
        Dashboard Operacional para empresa de locação de máquinas e venda de suprimentos
        """
        try:
            # Obter datas dos parâmetros
            data_inicial = datetime.strptime(request.query_params.get('dataInicial'), '%Y-%m-%d').date()
            data_final = datetime.strptime(request.query_params.get('dataFinal'), '%Y-%m-%d').date()

            # Filtros para consultas
            filtros = {
                'dataInicial': data_inicial.strftime('%Y-%m-%d'),
                'dataFinal': data_final.strftime('%Y-%m-%d'),
                'tipo': 'todos',
                'fonte': 'todos',
            }

            # Lançamentos financeiros
            lancamentos = FluxoCaixaLancamento.objects.filter(
                data__gte=data_inicial,
                data__lte=data_final
            )
            
            # Debug - Verificar categorias existentes
            categorias_existentes = lancamentos.filter(
                tipo='entrada',
                realizado=True
            ).values('categoria').distinct()

            # Cálculo de totalizadores
            totalizadores = {
                'entradas_realizadas': {
                    'valor': float(lancamentos.filter(tipo='entrada', realizado=True).aggregate(total=Sum('valor'))['total'] or 0),
                    'quantidade': lancamentos.filter(tipo='entrada', realizado=True).count(),
                    'percentual': None
                },
                'entradas_previstas': {
                    'valor': float(lancamentos.filter(tipo='entrada', realizado=False).aggregate(total=Sum('valor'))['total'] or 0),
                    'quantidade': lancamentos.filter(tipo='entrada', realizado=False).count(),
                    'percentual': None
                },
                'saidas_realizadas': {
                    'valor': float(lancamentos.filter(tipo='saida', realizado=True).aggregate(total=Sum('valor'))['total'] or 0),
                    'quantidade': lancamentos.filter(tipo='saida', realizado=True).count(),
                    'percentual': None
                },
                'saidas_previstas': {
                    'valor': float(lancamentos.filter(tipo='saida', realizado=False).aggregate(total=Sum('valor'))['total'] or 0),
                    'quantidade': lancamentos.filter(tipo='saida', realizado=False).count(),
                    'percentual': None
                }
            }

            # Cálculo de receitas por categoria
            lancamentos_entrada = lancamentos.filter(tipo='entrada', realizado=True)
            
            # Logging específico para cada categoria
            for categoria in categorias_existentes:
                total = lancamentos_entrada.filter(categoria=categoria['categoria']).aggregate(
                    quantidade=Count('id'),
                    valor=Sum('valor')
                )
                logger.info(f"Categoria {categoria}: {total['quantidade']} lançamentos, valor: {total['valor']}")
            
            receitas = {
                'vendas': float(lancamentos_entrada.filter(
                    categoria__in=['vendas']
                ).aggregate(total=Sum('valor'))['total'] or 0),
                
                'locacao': float(lancamentos_entrada.filter(
                    categoria__in=['aluguel', 'locacao_maquinas']
                ).aggregate(total=Sum('valor'))['total'] or 0),
                
                'servicos': float(lancamentos_entrada.filter(
                    categoria='servicos'
                ).aggregate(total=Sum('valor'))['total'] or 0),
                
                'manutencao': float(lancamentos_entrada.filter(
                    categoria='manutencao'
                ).aggregate(total=Sum('valor'))['total'] or 0),
                
                'suprimentos': float(lancamentos_entrada.filter(
                    categoria='suprimentos'
                ).aggregate(total=Sum('valor'))['total'] or 0)
            }

            # Movimentos detalhados ordenados por data
            movimentos = list(lancamentos.values(
                'id', 'data', 'tipo', 'valor', 'descricao', 
                'categoria', 'realizado', 'fonte_tipo', 'fonte_id'
            ).order_by('-data'))

            # Debug dos movimentos
            logger.info(f"Total de movimentos: {len(movimentos)}")
            if movimentos:
                logger.info(f"Exemplo de movimento: {movimentos[0]}")

            # Contratos e máquinas
            contratos = ContratosLocacao.objects.filter(
                inicio__lte=data_final,
                fim__gte=data_inicial
            )

            # Resumo do fluxo de caixa
            resumo = {
                'saldo_inicial': float(self._obter_saldo_inicial(data_inicial)),
                'saldo_final': float(self._obter_saldo_inicial(data_final)),
                'saldo_projetado': totalizadores['entradas_realizadas']['valor'] + totalizadores['entradas_previstas']['valor'] - \
                                (totalizadores['saidas_realizadas']['valor'] + totalizadores['saidas_previstas']['valor']),
                'variacao_percentual': 0,
                'entradas_total': totalizadores['entradas_realizadas']['valor'],
                'saidas_total': totalizadores['saidas_realizadas']['valor'],
                
                # Métricas específicas do negócio
                'vendas_equipamentos': receitas['vendas'],
                'alugueis_ativos': contratos.count(),
                'contratos_renovados': contratos.filter(renovado__isnull=False).count(),
                'servicos_total': receitas['servicos'] + receitas['manutencao'],
                'suprimentos_total': receitas['suprimentos'],
                
                # Detalhamento das receitas
                'receitas_detalhadas': receitas
            }

            # Calcula variação percentual se houver saldo inicial
            if resumo['saldo_inicial'] != 0:
                resumo['variacao_percentual'] = (
                    (resumo['saldo_final'] - resumo['saldo_inicial']) / 
                    resumo['saldo_inicial'] * 100
                )

            # Preparar resposta final
            resposta = {
                'filtros': filtros,
                'resumo': resumo,
                'movimentos': movimentos,
                'totalizadores': totalizadores,
                'categorias_encontradas': [c['categoria'] for c in categorias_existentes]
            }

            return Response(resposta)

        except Exception as e:
            logger.error(f"Erro no dashboard operacional: {str(e)}")
            logger.error(traceback.format_exc())
            
            return Response({
                'error': 'Falha ao processar dashboard operacional',
                'detalhes': str(e)
            }, status=400)
        
    @action(detail=False, methods=['GET'])
    def sincronizar_contas(self, request):
        """
        Endpoint para sincronizar contas a pagar, receber, notas fiscais e contratos
        """
        try:
            resultado = FluxoCaixaService.sincronizar_tudo()

            return Response({
                'status': 'sucesso',
                'mensagem': resultado
            })
        except Exception as e:
            return Response({
                'status': 'erro',
                'mensagem': str(e)
            }, status=400)
    
    def _obter_saldo_inicial(self, data):
        try:
            lancamentos_anteriores = self.get_queryset().filter(data__lt=data)
            
            saldo_inicial = lancamentos_anteriores.aggregate(
                saldo=Sum(
                    Case(
                        When(tipo='entrada', then='valor'),
                        When(tipo='saida', then=F('valor') * -1),
                        default=0,
                        output_field=DecimalField()
                    )
                )
            )['saldo'] or 0
            
            return float(saldo_inicial)
        
        except Exception as e:
            # Trate qualquer exceção que possa ocorrer
            print(f"Erro ao obter saldo inicial: {str(e)}")
            return 0

    def _analisar_fluxo_diario(self, lancamentos) -> List[Dict[str, Any]]:
        """Análise do fluxo diário de caixa"""
        return list(lancamentos.values(
            'data'
        ).annotate(
            entradas=Sum('valor', filter=Q(tipo='entrada')),
            saidas=Sum('valor', filter=Q(tipo='saida')),
            quantidade=Count('id'),
            realizados=Count('id', filter=Q(realizado=True))
        ).order_by('data'))

    def _analisar_status_pagamentos(self, lancamentos) -> Dict[str, Any]:
        """Análise do status dos pagamentos"""
        hoje = date.today()
        
        # Pagamentos em atraso
        atrasados = lancamentos.filter(
            realizado=False,
            data__lt=hoje
        ).aggregate(
            quantidade=Count('id'),
            valor_total=Sum('valor')
        )

        # Pagamentos do dia
        do_dia = lancamentos.filter(
            data=hoje
        ).aggregate(
            quantidade=Count('id'),
            valor_total=Sum('valor'),
            realizados=Count('id', filter=Q(realizado=True))
        )

        # Próximos vencimentos
        proximos = lancamentos.filter(
            data__gt=hoje,
            data__lte=hoje + timedelta(days=7)
        ).aggregate(
            quantidade=Count('id'),
            valor_total=Sum('valor')
        )

        return {
            'atrasados': {
                'quantidade': atrasados['quantidade'],
                'valor_total': float(atrasados['valor_total'] or 0)
            },
            'do_dia': {
                'quantidade': do_dia['quantidade'],
                'valor_total': float(do_dia['valor_total'] or 0),
                'realizados': do_dia['realizados']
            },
            'proximos': {
                'quantidade': proximos['quantidade'],
                'valor_total': float(proximos['valor_total'] or 0)
            }
        }

    def _gerar_alertas_operacionais(self, lancamentos) -> List[Dict[str, Any]]:
        """Gera alertas operacionais"""
        alertas = []
        hoje = date.today()

        # Alerta de atrasos
        atrasados = lancamentos.filter(
            realizado=False,
            data__lt=hoje
        ).count()
        
        if atrasados > 0:
            alertas.append({
                'tipo': 'atrasos',
                'severidade': 'alta' if atrasados > 10 else 'media',
                'mensagem': f'{atrasados} pagamentos em atraso',
                'detalhes': 'Verificar pagamentos atrasados'
            })

        # Alerta de concentração
        proximos_7dias = lancamentos.filter(
            data__range=[hoje, hoje + timedelta(days=7)]
        ).aggregate(total=Sum('valor'))['total'] or 0

        if proximos_7dias > 100000:  # Exemplo de threshold
            alertas.append({
                'tipo': 'concentracao',
                'severidade': 'media',
                'mensagem': f'Alta concentração de valores nos próximos 7 dias',
                'detalhes': f'R$ {proximos_7dias:.2f} a vencer'
            })

        return alertas

    def _calcular_indicadores_operacionais(self, lancamentos) -> Dict[str, Any]:
        """Calcula indicadores operacionais"""
        total_lancamentos = lancamentos.count()
        if total_lancamentos == 0:
            return {
                'realizacao': 0,
                'pontualidade': 0,
                'taxa_atrasos': 0
            }

        realizados = lancamentos.filter(realizado=True).count()
        pontuais = lancamentos.filter(
            realizado=True,
            data_realizacao=F('data')
        ).count()
        atrasados = lancamentos.filter(
            realizado=False,
            data__lt=date.today()
        ).count()

        return {
            'realizacao': realizados / total_lancamentos * 100,
            'pontualidade': pontuais / realizados * 100 if realizados > 0 else 0,
            'taxa_atrasos': atrasados / total_lancamentos * 100
        }

    @action(detail=False, methods=['GET'])
    def dashboard_gerencial(self, request):
        """
        Dashboard com informações gerenciais
        - Análise por período
        - Comparativos
        - Tendências
        - Indicadores estratégicos
        """
        try:
            # Parâmetros
            mes = int(request.query_params.get('mes', date.today().month))
            ano = int(request.query_params.get('ano', date.today().year))
            
            # Define período
            data_inicial = date(ano, mes, 1)
            data_final = date(ano, mes + 1, 1) - timedelta(days=1) if mes < 12 else date(ano + 1, 1, 1) - timedelta(days=1)

            # Busca lançamentos
            lancamentos = self.get_queryset().filter(
                data__range=[data_inicial, data_final]
            )

            # Busca período anterior para comparação
            mes_anterior = mes - 1 if mes > 1 else 12
            ano_anterior = ano if mes > 1 else ano - 1

            data_inicial_anterior = date(ano_anterior, mes_anterior, 1)
            data_final_anterior = date(ano_anterior, mes_anterior + 1, 1) - timedelta(days=1) if mes_anterior < 12 else date(ano, 1, 1) - timedelta(days=1)

            lancamentos_anterior = self.get_queryset().filter(
                data__range=[data_inicial_anterior, data_final_anterior]
            )

            # Análises
            resumo = self._gerar_resumo_gerencial(lancamentos, lancamentos_anterior)
            analise_categorias = self._analisar_categorias_gerencial(lancamentos)
            tendencias = self._analisar_tendencias_gerencial(lancamentos)
            indicadores = self._calcular_indicadores_gerenciais(lancamentos)

            return Response({
                'periodo': {
                    'mes': mes,
                    'ano': ano,
                    'inicio': data_inicial,
                    'fim': data_final
                },
                'resumo': resumo,
                'analise_categorias': analise_categorias,
                'tendencias': tendencias,
                'indicadores': indicadores,
                'recomendacoes': self._gerar_recomendacoes_gerenciais(
                    resumo, analise_categorias, tendencias, indicadores
                )
            })

        except Exception as e:
            return Response({'error': str(e)}, status=400)

    def _gerar_resumo_gerencial(self, lancamentos, lancamentos_anterior) -> Dict[str, Any]:
        """Gera resumo gerencial comparativo"""
        # Totais período atual
        totais_atual = lancamentos.aggregate(
            entradas=Sum('valor', filter=Q(tipo='entrada')),
            saidas=Sum('valor', filter=Q(tipo='saida'))
        )

        # Totais período anterior
        totais_anterior = lancamentos_anterior.aggregate(
            entradas=Sum('valor', filter=Q(tipo='entrada')),
            saidas=Sum('valor', filter=Q(tipo='saida'))
        )

        entradas_atual = totais_atual['entradas'] or 0
        entradas_anterior = totais_anterior['entradas'] or 1  # Evita divisão por zero
        saidas_atual = totais_atual['saidas'] or 0
        saidas_anterior = totais_anterior['saidas'] or 1

        return {
            'atual': {
                'entradas': float(entradas_atual),
                'saidas': float(saidas_atual),
                'resultado': float(entradas_atual - saidas_atual)
            },
            'anterior': {
                'entradas': float(totais_anterior['entradas'] or 0),
                'saidas': float(totais_anterior['saidas'] or 0),
                'resultado': float(
                    (totais_anterior['entradas'] or 0) - 
                    (totais_anterior['saidas'] or 0)
                )
            },
            'variacoes': {
                'entradas': (entradas_atual / entradas_anterior - 1) * 100,
                'saidas': (saidas_atual / saidas_anterior - 1) * 100
            }
        }

    def _analisar_categorias_gerencial(self, lancamentos) -> List[Dict[str, Any]]:
        """Análise gerencial por categorias"""
        return list(lancamentos.values(
            'categoria'
        ).annotate(
            entradas=Sum('valor', filter=Q(tipo='entrada')),
            saidas=Sum('valor', filter=Q(tipo='saida')),
            quantidade=Count('id'),
            media_valor=Avg('valor'),
            realizados=Count('id', filter=Q(realizado=True))
        ).order_by('-entradas'))

    def _analisar_tendencias_gerencial(self, lancamentos) -> Dict[str, Any]:
        """Análise de tendências gerenciais"""
        # Análise mensal
        tendencia_mensal = list(lancamentos.annotate(
            mes=TruncMonth('data')
        ).values('mes').annotate(
            entradas=Sum('valor', filter=Q(tipo='entrada')),
            saidas=Sum('valor', filter=Q(tipo='saida'))
        ).order_by('mes'))

        # Calcula projeções
        ultima_entrada = tendencia_mensal[-1]['entradas'] if tendencia_mensal else 0
        ultima_saida = tendencia_mensal[-1]['saidas'] if tendencia_mensal else 0

        return {
            'historico': tendencia_mensal,
            'projecoes': {
                'proximas_entradas': float(ultima_entrada * Decimal('1.1')),
                'proximas_saidas': float(ultima_saida * Decimal('1.1'))
            }
        }

    def _calcular_indicadores_gerenciais(self, lancamentos) -> Dict[str, Any]:
        """Calcula indicadores gerenciais"""
        # Totais
        totais = lancamentos.aggregate(
            entradas=Sum('valor', filter=Q(tipo='entrada')),
            saidas=Sum('valor', filter=Q(tipo='saida'))
        )

        entradas = totais['entradas'] or 0
        saidas = totais['saidas'] or 0

        # Margem
        margem = (
            ((entradas - saidas) / entradas) * 100
            if entradas > 0 else 0
        )

        return {
            'margem': float(margem),
            'realizacao_entradas': lancamentos.filter(
                    tipo='entrada',
                    realizado=True
                ).count() / lancamentos.filter(
                    tipo='entrada'
                ).count() * 100 if lancamentos.filter(tipo='entrada').exists() else 0,
            'realizacao_saidas': lancamentos.filter(
                    tipo='saida',
                    realizado=True
                ).count() / lancamentos.filter(
                    tipo='saida'
                ).count() * 100 if lancamentos.filter(tipo='saida').exists() else 0,
            'media_diaria_entradas': entradas / lancamentos.dates('data', 'day').count() if lancamentos.dates('data', 'day').count() > 0 else 0,
            'media_diaria_saidas': saidas / lancamentos.dates('data', 'day').count() if lancamentos.dates('data', 'day').count() > 0 else 0
        }

    def _gerar_recomendacoes_gerenciais(self, resumo, categorias, 
                                       tendencias, indicadores) -> List[Dict[str, str]]:
        """Gera recomendações baseadas nas análises gerenciais"""
        recomendacoes = []

        # Analisa variações
        if resumo['variacoes']['entradas'] < -10:
            recomendacoes.append({
                'tipo': 'receita',
                'severidade': 'alta',
                'mensagem': 'Queda significativa nas receitas',
                'acoes': [
                    'Revisar política comercial',
                    'Analisar causas da redução',
                    'Intensificar ações de vendas'
                ]
            })

        if resumo['variacoes']['saidas'] > 10:
            recomendacoes.append({
                'tipo': 'despesa',
                'severidade': 'alta',
                'mensagem': 'Aumento significativo nas despesas',
                'acoes': [
                    'Revisar principais gastos',
                    'Identificar oportunidades de redução',
                    'Implementar controles adicionais'
                ]
            })

        # Analisa margem
        if indicadores['margem'] < 20:
            recomendacoes.append({
                'tipo': 'margem',
                'severidade': 'media',
                'mensagem': 'Margem operacional abaixo do esperado',
                'acoes': [
                'Revisar precificação',
                'Analisar estrutura de custos',
                'Buscar eficiência operacional'
                ]
                })
            
            # Analisa realizações
        if indicadores['realizacao_entradas'] < 80:
            recomendacoes.append({
                'tipo': 'realizacao',
                'severidade': 'media',
                'mensagem': 'Baixa realização de receitas previstas',
                'acoes': [
                    'Revisar processo de cobrança',
                    'Analisar inadimplência',
                    'Ajustar previsões'
                ]
            })

        return recomendacoes

    @action(detail=False, methods=['GET'])
    def dashboard_consolidado(self, request):
        """
        Dashboard consolidado com principais indicadores
        - Visão geral
        - Principais métricas
        - Destaques
        - Comparativos
        """
        try:
            # Parâmetros
            periodo = int(request.query_params.get('periodo', 30))
            data_final = date.today()
            data_inicial = data_final - timedelta(days=periodo)

            # Busca lançamentos
            lancamentos = self.get_queryset().filter(
                data__range=[data_inicial, data_final]
            )

            # Gera visões
            visao_geral = self._gerar_visao_geral(lancamentos)
            metricas = self._calcular_metricas_consolidadas(lancamentos)
            destaques = self._identificar_destaques(lancamentos)
            comparativos = self._gerar_comparativos(lancamentos)

            return Response({
                'periodo': {
                    'inicio': data_inicial,
                    'fim': data_final,
                    'dias': periodo
                },
                'visao_geral': visao_geral,
                'metricas': metricas,
                'destaques': destaques,
                'comparativos': comparativos
            })

        except Exception as e:
            return Response({'error': str(e)}, status=400)

    def _gerar_visao_geral(self, lancamentos) -> Dict[str, Any]:
        """Gera visão geral do período"""
        totais = lancamentos.aggregate(
            total_lancamentos=Count('id'),
            entradas=Sum('valor', filter=Q(tipo='entrada')),
            saidas=Sum('valor', filter=Q(tipo='saida')),
            realizados=Count('id', filter=Q(realizado=True))
        )

        return {
            'total_lancamentos': totais['total_lancamentos'],
            'total_entradas': float(totais['entradas'] or 0),
            'total_saidas': float(totais['saidas'] or 0),
            'percentual_realizado': totais['realizados'] / totais['total_lancamentos'] * 100 if totais['total_lancamentos'] > 0 else 0
        }

    def _calcular_metricas_consolidadas(self, lancamentos) -> Dict[str, Any]:
        """Calcula métricas consolidadas do período"""
        hoje = date.today()

        return {
            'fluxo': {
                'saldo_atual': float(self._obter_saldo_inicial(hoje)),
                'previsao_proximos_dias': float(
                    lancamentos.filter(
                        data__gt=hoje
                    ).aggregate(
                        total=Sum(
                            F('valor'),
                            filter=Q(tipo='entrada')
                        ) - Sum(
                            F('valor'),
                            filter=Q(tipo='saida')
                        )
                    )['total'] or 0
                )
            },
            'operacional': {
                'media_diaria_lancamentos': lancamentos.count() / lancamentos.dates('data', 'day').count() if lancamentos.dates('data', 'day').count() > 0 else 0,
                'ticket_medio_entradas': float(
                    lancamentos.filter(tipo='entrada').aggregate(
                        avg=Avg('valor')
                    )['avg'] or 0
                )
            },
            'realizacao': {
                'percentual_entradas': lancamentos.filter(
                        tipo='entrada',
                        realizado=True
                    ).count() / lancamentos.filter(
                        tipo='entrada'
                    ).count() * 100 if lancamentos.filter(tipo='entrada').exists() else 0,
                'percentual_saidas': lancamentos.filter(
                        tipo='saida',
                        realizado=True
                    ).count() / lancamentos.filter(
                        tipo='saida'
                    ).count() * 100 if lancamentos.filter(tipo='saida').exists() else 0
            }
        }

    def _identificar_destaques(self, lancamentos) -> Dict[str, Any]:
        """Identifica destaques do período"""
        return {
            'maiores_entradas': list(lancamentos.filter(
                tipo='entrada'
            ).order_by('-valor').values(
                'data', 'descricao', 'valor', 'categoria'
            )[:5]),
            'maiores_saidas': list(lancamentos.filter(
                tipo='saida'
            ).order_by('-valor').values(
                'data', 'descricao', 'valor', 'categoria'
            )[:5]),
            'categorias_relevantes': list(lancamentos.values(
                'categoria'
            ).annotate(
                total=Sum('valor')
            ).order_by('-total')[:5]),
            'dias_relevantes': list(lancamentos.values(
                'data'
            ).annotate(
                data_ref=TruncDate('data'),
                total=Sum('valor')
            ).values('data_ref', 'total').order_by('-total')[:5])
        }

    def _gerar_comparativos(self, lancamentos) -> Dict[str, Any]:
        """Gera comparativos com períodos anteriores"""
        periodo_dias = (lancamentos.latest('data').data - 
                    lancamentos.earliest('data').data).days
        
        data_inicial_anterior = lancamentos.earliest('data').data - timedelta(days=periodo_dias)
        
        lancamentos_anterior = self.get_queryset().filter(
            data__range=[data_inicial_anterior, 
                        lancamentos.earliest('data').data - timedelta(days=1)]
        )

        return {
            'periodo_anterior': {
                'total_lancamentos': lancamentos_anterior.count(),
                'total_entradas': float(
                    lancamentos_anterior.filter(
                        tipo='entrada'
                    ).aggregate(
                        total=Sum('valor')
                    )['total'] or 0
                ),
                'total_saidas': float(
                    lancamentos_anterior.filter(
                        tipo='saida'
                    ).aggregate(
                        total=Sum('valor')
                    )['total'] or 0
                )
            },
            'variacoes': {
                'quantidade': (lancamentos.count() / lancamentos_anterior.count() - 1) * 100 if lancamentos_anterior.count() > 0 else 0,
                'entradas': ((lancamentos.filter(tipo='entrada').aggregate(total=Sum('valor'))['total'] or 0) / (lancamentos_anterior.filter(tipo='entrada').aggregate(total=Sum('valor'))['total'] or 1) - 1) * 100,
                'saidas': ((lancamentos.filter(tipo='saida').aggregate(total=Sum('valor'))['total'] or 0) / (lancamentos_anterior.filter(tipo='saida').aggregate(total=Sum('valor'))['total'] or 1) - 1) * 100           
            }
        }