# empresa/contas/views/analise_fluxo_caixa.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum, Count, Avg
from django.db.models.functions import TruncMonth
from datetime import datetime, date, timedelta
from decimal import Decimal
import time

from ..models.access import ContasPagar, ContasReceber


class AnaliseFluxoCaixaViewSet(viewsets.ViewSet):
    """
    ViewSet para análise comparativa do fluxo de caixa (realizado vs previsto)
    """

    def parse_date(self, date_str):
        """
        Converte string de data ISO para objeto date
        """
        if not date_str:
            return None
        try:
            date_str = date_str.split('T')[0]
            return date(*time.strptime(date_str, '%Y-%m-%d')[:3])
        except (ValueError, IndexError):
            return None

    @action(detail=False, methods=['get'])
    def comparativo_realizado_vs_previsto(self, request):
        """
        Compara fluxo de caixa realizado vs previsto no período
        """
        data_inicio = self.parse_date(request.query_params.get('data_inicio'))
        data_fim = self.parse_date(request.query_params.get('data_fim'))
        
        if not data_inicio or not data_fim:
            return Response(
                {'error': 'Parâmetros data_inicio e data_fim são obrigatórios (formato: YYYY-MM-DD)'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # === DADOS REALIZADOS ===
        # Contas pagas (realizadas)
        contas_pagas = ContasPagar.objects.filter(
            data_pagamento__isnull=False,
            data_pagamento__date__gte=data_inicio,
            data_pagamento__date__lte=data_fim,
            status='P'
        ).aggregate(
            total_pago=Sum('valor_pago'),
            quantidade=Count('id')
        )

        # Contas recebidas (realizadas)
        contas_recebidas = ContasReceber.objects.filter(
            data_pagamento__isnull=False,
            data_pagamento__date__gte=data_inicio,
            data_pagamento__date__lte=data_fim,
            status='P'
        ).aggregate(
            total_recebido=Sum('recebido'),
            quantidade=Count('id')
        )

        # === DADOS PREVISTOS ===
        # Contas a pagar vencidas no período (mas ainda não pagas)
        contas_previstas_pagar = ContasPagar.objects.filter(
            vencimento__date__gte=data_inicio,
            vencimento__date__lte=data_fim,
            status='A'  # Status aberto
        ).aggregate(
            total_previsto=Sum('valor'),
            quantidade=Count('id')
        )

        # Contas a receber vencidas no período (mas ainda não recebidas)
        contas_previstas_receber = ContasReceber.objects.filter(
            vencimento__date__gte=data_inicio,
            vencimento__date__lte=data_fim,
            status='A'  # Status aberto
        ).aggregate(
            total_previsto=Sum('valor'),
            quantidade=Count('id')
        )

        # Calcular totais
        total_realizado_entradas = float(contas_recebidas['total_recebido'] or 0)
        total_realizado_saidas = float(contas_pagas['total_pago'] or 0)
        total_previsto_entradas = float(contas_previstas_receber['total_previsto'] or 0)
        total_previsto_saidas = float(contas_previstas_pagar['total_previsto'] or 0)

        saldo_realizado = total_realizado_entradas - total_realizado_saidas
        saldo_previsto = total_previsto_entradas - total_previsto_saidas

        # Calcular percentuais de realização
        perc_realizacao_entradas = 0
        if total_previsto_entradas > 0:
            perc_realizacao_entradas = (total_realizado_entradas / total_previsto_entradas) * 100

        perc_realizacao_saidas = 0
        if total_previsto_saidas > 0:
            perc_realizacao_saidas = (total_realizado_saidas / total_previsto_saidas) * 100

        return Response({
            'periodo': {
                'data_inicio': data_inicio.strftime('%Y-%m-%d'),
                'data_fim': data_fim.strftime('%Y-%m-%d')
            },
            'realizado': {
                'entradas': total_realizado_entradas,
                'saidas': total_realizado_saidas,
                'saldo_liquido': saldo_realizado,
                'qtd_contas_recebidas': contas_recebidas['quantidade'],
                'qtd_contas_pagas': contas_pagas['quantidade']
            },
            'previsto': {
                'entradas': total_previsto_entradas,
                'saidas': total_previsto_saidas,
                'saldo_liquido': saldo_previsto,
                'qtd_contas_a_receber': contas_previstas_receber['quantidade'],
                'qtd_contas_a_pagar': contas_previstas_pagar['quantidade']
            },
            'analise': {
                'diferenca_entradas': total_realizado_entradas - total_previsto_entradas,
                'diferenca_saidas': total_realizado_saidas - total_previsto_saidas,
                'diferenca_saldo': saldo_realizado - saldo_previsto,
                'percentual_realizacao_entradas': round(perc_realizacao_entradas, 2),
                'percentual_realizacao_saidas': round(perc_realizacao_saidas, 2)
            }
        })

    @action(detail=False, methods=['get'])
    def inadimplencia(self, request):
        """
        Análise de inadimplência - contas vencidas não pagas/recebidas
        """
        data_limite = self.parse_date(request.query_params.get('data_limite'))
        
        if not data_limite:
            data_limite = date.today()

        # Contas a pagar em atraso
        contas_pagar_atraso = ContasPagar.objects.filter(
            vencimento__date__lt=data_limite,
            status='A',
            data_pagamento__isnull=True
        ).values(
            'id', 'vencimento', 'valor', 'fornecedor__nome', 'historico'
        ).annotate(
            dias_atraso=data_limite - F('vencimento__date')
        )

        # Contas a receber em atraso
        contas_receber_atraso = ContasReceber.objects.filter(
            vencimento__date__lt=data_limite,
            status='A',
            data_pagamento__isnull=True
        ).values(
            'id', 'vencimento', 'valor', 'cliente__nome', 'historico'
        ).annotate(
            dias_atraso=data_limite - F('vencimento__date')
        )

        # Calcular totais
        total_pagar_atraso = ContasPagar.objects.filter(
            vencimento__date__lt=data_limite,
            status='A',
            data_pagamento__isnull=True
        ).aggregate(
            total=Sum('valor'),
            quantidade=Count('id')
        )

        total_receber_atraso = ContasReceber.objects.filter(
            vencimento__date__lt=data_limite,
            status='A',
            data_pagamento__isnull=True
        ).aggregate(
            total=Sum('valor'),
            quantidade=Count('id')
        )

        # Agrupar por faixas de atraso
        faixas_atraso = [
            {'nome': '1-30 dias', 'min': 1, 'max': 30},
            {'nome': '31-60 dias', 'min': 31, 'max': 60},
            {'nome': '61-90 dias', 'min': 61, 'max': 90},
            {'nome': 'Mais de 90 dias', 'min': 91, 'max': 999999}
        ]

        analise_faixas = []
        for faixa in faixas_atraso:
            data_min = data_limite - timedelta(days=faixa['max'])
            data_max = data_limite - timedelta(days=faixa['min'])
            
            pagar_faixa = ContasPagar.objects.filter(
                vencimento__date__gte=data_min,
                vencimento__date__lte=data_max,
                status='A',
                data_pagamento__isnull=True
            ).aggregate(
                total=Sum('valor'),
                quantidade=Count('id')
            )
            
            receber_faixa = ContasReceber.objects.filter(
                vencimento__date__gte=data_min,
                vencimento__date__lte=data_max,
                status='A',
                data_pagamento__isnull=True
            ).aggregate(
                total=Sum('valor'),
                quantidade=Count('id')
            )
            
            analise_faixas.append({
                'faixa': faixa['nome'],
                'contas_pagar': {
                    'total': float(pagar_faixa['total'] or 0),
                    'quantidade': pagar_faixa['quantidade']
                },
                'contas_receber': {
                    'total': float(receber_faixa['total'] or 0),
                    'quantidade': receber_faixa['quantidade']
                }
            })

        return Response({
            'data_referencia': data_limite.strftime('%Y-%m-%d'),
            'resumo': {
                'total_contas_pagar_atraso': float(total_pagar_atraso['total'] or 0),
                'qtd_contas_pagar_atraso': total_pagar_atraso['quantidade'],
                'total_contas_receber_atraso': float(total_receber_atraso['total'] or 0),
                'qtd_contas_receber_atraso': total_receber_atraso['quantidade'],
                'impacto_saldo': float(total_receber_atraso['total'] or 0) - float(total_pagar_atraso['total'] or 0)
            },
            'analise_por_faixas': analise_faixas,
            'detalhes': {
                'contas_pagar_atraso': list(contas_pagar_atraso)[:50],  # Limitar a 50 registros
                'contas_receber_atraso': list(contas_receber_atraso)[:50]  # Limitar a 50 registros
            }
        })

    @action(detail=False, methods=['get'])
    def projecao_semanal(self, request):
        """
        Projeção do fluxo de caixa para as próximas semanas
        """
        semanas = int(request.query_params.get('semanas', 4))  # Default 4 semanas
        data_inicio = date.today()
        
        projecoes = []
        
        for i in range(semanas):
            inicio_semana = data_inicio + timedelta(weeks=i)
            fim_semana = inicio_semana + timedelta(days=6)
            
            # Contas a pagar na semana
            pagar_semana = ContasPagar.objects.filter(
                vencimento__date__gte=inicio_semana,
                vencimento__date__lte=fim_semana,
                status='A'
            ).aggregate(
                total=Sum('valor'),
                quantidade=Count('id')
            )
            
            # Contas a receber na semana
            receber_semana = ContasReceber.objects.filter(
                vencimento__date__gte=inicio_semana,
                vencimento__date__lte=fim_semana,
                status='A'
            ).aggregate(
                total=Sum('valor'),
                quantidade=Count('id')
            )
            
            total_entradas = float(receber_semana['total'] or 0)
            total_saidas = float(pagar_semana['total'] or 0)
            saldo_semana = total_entradas - total_saidas
            
            projecoes.append({
                'semana': i + 1,
                'periodo': {
                    'inicio': inicio_semana.strftime('%Y-%m-%d'),
                    'fim': fim_semana.strftime('%Y-%m-%d')
                },
                'entradas_previstas': total_entradas,
                'saidas_previstas': total_saidas,
                'saldo_previsto': saldo_semana,
                'qtd_contas_receber': receber_semana['quantidade'],
                'qtd_contas_pagar': pagar_semana['quantidade']
            })
        
        # Calcular totais gerais
        total_entradas_projetadas = sum(p['entradas_previstas'] for p in projecoes)
        total_saidas_projetadas = sum(p['saidas_previstas'] for p in projecoes)
        saldo_total_projetado = total_entradas_projetadas - total_saidas_projetadas
        
        return Response({
            'periodo_projecao': f"{semanas} semanas",
            'resumo_geral': {
                'total_entradas_projetadas': total_entradas_projetadas,
                'total_saidas_projetadas': total_saidas_projetadas,
                'saldo_total_projetado': saldo_total_projetado
            },
            'projecoes_semanais': projecoes
        })

from django.db.models import F
