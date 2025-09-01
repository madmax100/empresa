# empresa/contas/mixins/fluxo_caixa/analise.py
from typing import Dict, Any, List
from decimal import Decimal
from datetime import date, datetime, timedelta
from django.db.models import Sum, F, Q, Count, Case, When, Avg, DecimalField, ExpressionWrapper
from django.db.models.functions import ExtractMonth, ExtractYear, ExtractDay, Coalesce
from django.utils import timezone

class FluxoCaixaAnaliseMixin:
    """
    Mixin para análises e relatórios do fluxo de caixa
    """
    def _calcular_indicadores(self, lancamentos, ano: int) -> Dict[str, Any]:
        """Calcula indicadores financeiros do período"""
        hoje = timezone.now().date()
        
        try:
            return {
                'liquidez': self._calcular_liquidez(lancamentos),
                'ciclo_financeiro': self._calcular_ciclo_financeiro(lancamentos, hoje),
                'concentracao_receitas': self._calcular_concentracao_receitas(lancamentos),
                'crescimento': self._calcular_crescimento(lancamentos, ano),
                'indicadores_adicionais': self._calcular_indicadores_adicionais(lancamentos, hoje)
            }
        except Exception as e:
            print(f"Erro ao calcular indicadores: {str(e)}")
            return {
                'liquidez': Decimal('0'),
                'ciclo_financeiro': Decimal('0'),
                'concentracao_receitas': {},
                'crescimento': Decimal('0'),
                'indicadores_adicionais': {}
            }

    def _calcular_liquidez(self, lancamentos) -> Dict[str, Decimal]:
        """
        Calcula índices de liquidez
        - Liquidez imediata: Disponibilidades / Passivo Circulante
        - Liquidez corrente: Ativo Circulante / Passivo Circulante
        """
        hoje = timezone.now().date()
        proximo_mes = hoje + timedelta(days=30)
        
        # Saldo disponível
        disponibilidades = lancamentos.filter(
            realizado=True,
            tipo='entrada',
            data__lte=hoje
        ).aggregate(
            total=Coalesce(Sum('valor'), Decimal('0'))
        )['total']
        
        disponibilidades -= lancamentos.filter(
            realizado=True,
            tipo='saida',
            data__lte=hoje
        ).aggregate(
            total=Coalesce(Sum('valor'), Decimal('0'))
        )['total']

        # Passivo circulante (compromissos dos próximos 30 dias)
        passivo_circulante = lancamentos.filter(
            tipo='saida',
            data__range=[hoje, proximo_mes]
        ).aggregate(
            total=Coalesce(Sum('valor'), Decimal('1'))
        )['total']

        # Ativo circulante (disponibilidades + recebíveis 30 dias)
        recebiveis = lancamentos.filter(
            tipo='entrada',
            data__range=[hoje, proximo_mes]
        ).aggregate(
            total=Coalesce(Sum('valor'), Decimal('0'))
        )['total']
        
        ativo_circulante = disponibilidades + recebiveis

        return {
            'liquidez_imediata': disponibilidades / passivo_circulante,
            'liquidez_corrente': ativo_circulante / passivo_circulante
        }

    def _calcular_ciclo_financeiro(self, lancamentos, data_ref: date) -> Dict[str, Decimal]:
        """
        Calcula o ciclo financeiro
        - Prazo médio de recebimento
        - Prazo médio de pagamento
        - Ciclo financeiro total
        """
        # Recebimentos realizados
        pmr = lancamentos.filter(
            tipo='entrada',
            realizado=True,
            data_realizacao__isnull=False
        ).annotate(
            prazo=ExtractDay(F('data_realizacao') - F('data'))
        ).aggregate(
            media=Coalesce(Avg('prazo'), Decimal('0'))
        )['media']

        # Pagamentos realizados
        pmp = lancamentos.filter(
            tipo='saida',
            realizado=True,
            data_realizacao__isnull=False
        ).annotate(
            prazo=ExtractDay(F('data_realizacao') - F('data'))
        ).aggregate(
            media=Coalesce(Avg('prazo'), Decimal('0'))
        )['media']

        return {
            'prazo_medio_recebimento': pmr,
            'prazo_medio_pagamento': pmp,
            'ciclo_financeiro': pmr - pmp
        }

    def _calcular_concentracao_receitas(self, lancamentos) -> Dict[str, Any]:
        """
        Calcula a concentração de receitas
        - Por categoria
        - Por cliente
        - Por tipo de operação
        """
        # Total de receitas
        total_receitas = lancamentos.filter(
            tipo='entrada'
        ).aggregate(
            total=Coalesce(Sum('valor'), Decimal('0'))
        )['total']

        # Concentração por categoria
        categorias = lancamentos.filter(
            tipo='entrada'
        ).values('categoria').annotate(
            total=Sum('valor'),
            percentual=ExpressionWrapper(
                Sum('valor') * 100 / total_receitas,
                output_field=DecimalField()
            )
        ).order_by('-total')

        # Concentração por cliente
        clientes = lancamentos.filter(
            tipo='entrada',
            cliente__isnull=False
        ).values(
            'cliente',
            'cliente__nome'
        ).annotate(
            total=Sum('valor'),
            percentual=ExpressionWrapper(
                Sum('valor') * 100 / total_receitas,
                output_field=DecimalField()
            )
        ).order_by('-total')

        return {
            'categorias': list(categorias),
            'clientes': list(clientes),
            'total_receitas': total_receitas
        }

    def _calcular_crescimento(self, lancamentos, ano: int) -> Dict[str, Any]:
        """
        Calcula indicadores de crescimento
        - Crescimento mensal
        - Crescimento anual
        - Projeção anual
        """
        hoje = timezone.now().date()
        
        # Análise mensal
        mes_atual = lancamentos.filter(
            tipo='entrada',
            data__year=hoje.year,
            data__month=hoje.month
        ).aggregate(
            total=Coalesce(Sum('valor'), Decimal('0'))
        )['total']

        mes_anterior = lancamentos.filter(
            tipo='entrada',
            data__year=(hoje - timedelta(days=30)).year,
            data__month=(hoje - timedelta(days=30)).month
        ).aggregate(
            total=Coalesce(Sum('valor'), Decimal('0'))
        )['total']

        # Análise anual
        ano_atual = lancamentos.filter(
            tipo='entrada',
            data__year=hoje.year
        ).aggregate(
            total=Coalesce(Sum('valor'), Decimal('0'))
        )['total']

        ano_anterior = lancamentos.filter(
            tipo='entrada',
            data__year=hoje.year-1
        ).aggregate(
            total=Coalesce(Sum('valor'), Decimal('0'))
        )['total']

        # Cálculo dos percentuais
        crescimento_mensal = ((mes_atual / mes_anterior) - 1) * 100 if mes_anterior else 0
        crescimento_anual = ((ano_atual / ano_anterior) - 1) * 100 if ano_anterior else 0

        return {
            'crescimento_mensal': crescimento_mensal,
            'crescimento_anual': crescimento_anual,
            'valores': {
                'mes_atual': mes_atual,
                'mes_anterior': mes_anterior,
                'ano_atual': ano_atual,
                'ano_anterior': ano_anterior
            }
        }

    def _calcular_indicadores_adicionais(self, lancamentos, data_ref: date) -> Dict[str, Any]:
        """
        Calcula indicadores adicionais específicos do negócio
        - Margem operacional
        - Índice de inadimplência
        - Taxa de renovação de contratos
        """
        # Margem operacional
        receitas = lancamentos.filter(
            tipo='entrada',
            realizado=True,
            data__year=data_ref.year,
            data__month=data_ref.month
        ).aggregate(
            total=Coalesce(Sum('valor'), Decimal('0'))
        )['total']

        custos = lancamentos.filter(
            tipo='saida',
            realizado=True,
            data__year=data_ref.year,
            data__month=data_ref.month
        ).aggregate(
            total=Coalesce(Sum('valor'), Decimal('0'))
        )['total']

        # Inadimplência
        vencidos = lancamentos.filter(
            tipo='entrada',
            realizado=False,
            data__lt=data_ref
        ).aggregate(
            total=Coalesce(Sum('valor'), Decimal('0'))
        )['total']

        total_recebiveis = lancamentos.filter(
            tipo='entrada',
            data__lt=data_ref
        ).aggregate(
            total=Coalesce(Sum('valor'), Decimal('1'))
        )['total']

        return {
            'margem_operacional': ((receitas - custos) / receitas * 100) if receitas else 0,
            'indice_inadimplencia': (vencidos / total_recebiveis * 100) if total_recebiveis else 0,
            'valores': {
                'receitas': receitas,
                'custos': custos,
                'vencidos': vencidos,
                'total_recebiveis': total_recebiveis
            }
        }