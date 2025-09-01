# Imports necessários
from django.db import models
from django.db.models import Sum, Count, Avg, Q, F, Value, Case, When, ExpressionWrapper
from django.db.models.functions import TruncMonth, ExtractMonth, ExtractYear, ExtractDay, Coalesce
from django.forms import FloatField
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime, timedelta
from decimal import Decimal
from collections import defaultdict

from contas.models.fluxo_caixa import FluxoCaixaLancamento, SaldoDiario

class DashboardEstrategicoMixin:
    
    def get_date_range(self):
        """Retorna o range de datas para análise"""
        hoje = timezone.now().date()
        inicio = hoje - timedelta(days=365)  # 1 ano atrás
        fim = hoje + timedelta(days=180)     # 6 meses futuros
        return inicio, fim, hoje

    @action(detail=False, methods=['get'])
    def dashboard_estrategico(self, request):
        """
        Dashboard com informações estratégicas alinhadas com o frontend
        """
        try:
            inicio, fim, hoje = self.get_date_range()
            
            # Buscar lançamentos do período
            lancamentos = FluxoCaixaLancamento.objects.filter(
                data__range=(inicio, fim)
            ).exclude(
                data_estorno__isnull=False
            )

            # Calcula DRE
            dre = self._calcular_dre(lancamentos, hoje)
            
            # Análise de tendências
            tendencias = self._calcular_tendencias(lancamentos, hoje)
            
            # Projeções futuras
            projecoes = self._calcular_projecoes(lancamentos, hoje)
            
            # Indicadores estratégicos
            indicadores = self._calcular_indicadores(lancamentos, hoje)

            return Response({
                'dre': dre,
                'tendencias': tendencias,
                'projecoes': projecoes,
                'indicadores': indicadores
            })

        except Exception as e:
            return Response({'error': str(e)}, status=400)

    def _calcular_dre(self, lancamentos, data_ref):
        """Calcula o DRE do período"""
        mes_atual = lancamentos.filter(
            data__year=data_ref.year,
            data__month=data_ref.month,
            realizado=True
        )

        # Receitas
        receita_bruta = mes_atual.filter(
            tipo='entrada',
            categoria__in=['vendas', 'aluguel', 'servicos']
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')

        # Deduções (impostos sobre receita)
        deducoes = mes_atual.filter(
            tipo='saida',
            categoria='impostos'
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')

        # Custos operacionais
        custos = mes_atual.filter(
            tipo='saida',
            categoria__in=['suprimentos', 'manutencao', 'locacao_maquinas']
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')

        # Despesas operacionais
        despesas = mes_atual.filter(
            tipo='saida',
            categoria__in=['despesas_operacionais', 'despesas_administrativas', 'folha_pagamento']
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')

        receita_liquida = receita_bruta - deducoes
        resultado_operacional = receita_liquida - custos - despesas

        return {
            'receita_bruta': float(receita_bruta),
            'deducoes': float(deducoes),
            'receita_liquida': float(receita_liquida),
            'custos_operacionais': float(custos),
            'despesas_operacionais': float(despesas),
            'resultado_operacional': float(resultado_operacional),
            'receitas_financeiras': 0,  # Implementar se necessário
            'despesas_financeiras': 0,  # Implementar se necessário
            'resultado_antes_impostos': float(resultado_operacional),
            'impostos': float(deducoes),
            'resultado_liquido': float(resultado_operacional - deducoes)
        }

    def _calcular_tendencias(self, lancamentos, data_ref):
        """Calcula tendências de receitas, despesas e saldos"""
        # Análise dos últimos 6 meses
        inicio_analise = data_ref - timedelta(days=180)
        
        tendencia_mensal = lancamentos.filter(
            data__gte=inicio_analise,
            data__lte=data_ref,
            realizado=True
        ).annotate(
            mes=TruncMonth('data')
        ).values('mes', 'tipo').annotate(
            total=Sum('valor')
        ).order_by('mes', 'tipo')

        # Organiza dados por tipo
        receitas = []
        despesas = []
        saldos = []

        meses_unicos = sorted(set(item['mes'] for item in tendencia_mensal))
        
        for mes in meses_unicos:
            # Valores realizados
            entradas = sum(float(item['total']) for item in tendencia_mensal 
                         if item['mes'] == mes and item['tipo'] == 'entrada')
            saidas = sum(float(item['total']) for item in tendencia_mensal 
                        if item['mes'] == mes and item['tipo'] == 'saida')
            
            # Valores previstos (do mês seguinte)
            previsao_mes = lancamentos.filter(
                data__month=mes.month + 1 if mes.month < 12 else 1,
                data__year=mes.year if mes.month < 12 else mes.year + 1
            )
            
            entradas_previstas = float(previsao_mes.filter(tipo='entrada')
                                     .aggregate(total=Sum('valor'))['total'] or 0)
            saidas_previstas = float(previsao_mes.filter(tipo='saida')
                                   .aggregate(total=Sum('valor'))['total'] or 0)

            # Calcula variações
            var_receitas = ((entradas_previstas - entradas) / entradas * 100 
                          if entradas > 0 else 0)
            var_despesas = ((saidas_previstas - saidas) / saidas * 100 
                          if saidas > 0 else 0)
            var_saldo = (((entradas_previstas - saidas_previstas) - (entradas - saidas)) / 
                        (entradas - saidas) * 100 if (entradas - saidas) != 0 else 0)

            # Define tendências
            def get_tendencia(variacao):
                if variacao > 5:
                    return 'alta'
                elif variacao < -5:
                    return 'baixa'
                return 'estavel'

            # Adiciona aos arrays de resposta
            receitas.append({
                'periodo': mes.strftime('%Y-%m'),
                'valor_realizado': entradas,
                'valor_previsto': entradas_previstas,
                'variacao_percentual': round(var_receitas, 2),
                'tendencia': get_tendencia(var_receitas)
            })

            despesas.append({
                'periodo': mes.strftime('%Y-%m'),
                'valor_realizado': saidas,
                'valor_previsto': saidas_previstas,
                'variacao_percentual': round(var_despesas, 2),
                'tendencia': get_tendencia(var_despesas)
            })

            saldos.append({
                'periodo': mes.strftime('%Y-%m'),
                'valor_realizado': entradas - saidas,
                'valor_previsto': entradas_previstas - saidas_previstas,
                'variacao_percentual': round(var_saldo, 2),
                'tendencia': get_tendencia(var_saldo)
            })

        return {
            'receitas': receitas,
            'despesas': despesas,
            'saldos': saldos
        }

    def _calcular_projecoes(self, lancamentos, data_ref):
        """Calcula projeções para diferentes períodos"""
        def calcular_resumo(inicio, fim):
            periodo = lancamentos.filter(data__range=(inicio, fim))
            
            entradas = float(periodo.filter(tipo='entrada')
                           .aggregate(total=Sum('valor'))['total'] or 0)
            saidas = float(periodo.filter(tipo='saida')
                         .aggregate(total=Sum('valor'))['total'] or 0)
            
            # Calcula valores específicos do negócio
            vendas = float(periodo.filter(tipo='entrada', categoria='vendas')
                         .aggregate(total=Sum('valor'))['total'] or 0)
            alugueis = float(periodo.filter(tipo='entrada', categoria='aluguel')
                           .aggregate(total=Sum('valor'))['total'] or 0)
            
            return {
                'saldo_inicial': self._obter_saldo_inicial(inicio),
                'saldo_final': entradas - saidas,
                'saldo_projetado': entradas - saidas,
                'variacao_percentual': ((entradas - saidas) / entradas * 100 
                                      if entradas > 0 else 0),
                'entradas_total': entradas,
                'saidas_total': saidas,
                'vendas_equipamentos': vendas,
                'alugueis_ativos': alugueis,
                'contratos_renovados': 0,  # Implementar se necessário
                'servicos_total': float(periodo.filter(tipo='entrada', categoria='servicos')
                                      .aggregate(total=Sum('valor'))['total'] or 0),
                'suprimentos_total': float(periodo.filter(tipo='saida', categoria='suprimentos')
                                         .aggregate(total=Sum('valor'))['total'] or 0)
            }

        return {
            'proximos_30_dias': calcular_resumo(
                data_ref, 
                data_ref + timedelta(days=30)
            ),
            'proximos_90_dias': calcular_resumo(
                data_ref, 
                data_ref + timedelta(days=90)
            ),
            'proximos_180_dias': calcular_resumo(
                data_ref, 
                data_ref + timedelta(days=180)
            )
        }

    def _calcular_indicadores(self, lancamentos, data_ref):
        """Calcula indicadores estratégicos"""
        try:
            # 1. Liquidez imediata
            saldo_atual = self._obter_saldo_inicial(data_ref)
            compromissos = float(
                lancamentos.filter(
                    data__range=(data_ref, data_ref + timedelta(days=30)),
                    tipo='saida'
                ).aggregate(total=Sum('valor'))['total'] or 0
            )
            
            # Definir tipo para liquidez
            liquidez = ExpressionWrapper(
                Value(saldo_atual) / Value(compromissos),
                output_field=FloatField()
            ) if compromissos > 0 else 0

            # 2. Ciclo de caixa
            pmt_recebimento = lancamentos.filter(
                tipo='entrada',
                realizado=True,
                data_realizacao__isnull=False
            ).aggregate(
                media=ExpressionWrapper(
                    Avg('prazo'),
                    output_field=FloatField()
                )
            )['media'] or 0

            pmt_pagamento = lancamentos.filter(
                tipo='saida',
                realizado=True,
                data_realizacao__isnull=False
            ).aggregate(
                media=ExpressionWrapper(
                    Avg('prazo'),
                    output_field=FloatField()
                )
            )['media'] or 0

            ciclo_caixa = ExpressionWrapper(
                Value(pmt_recebimento) - Value(pmt_pagamento),
                output_field=FloatField()
            )

            # 3. Margem operacional
            dre = self._calcular_dre(lancamentos, data_ref)
            receita_bruta = float(dre['receita_bruta'])
            resultado_operacional = float(dre['resultado_operacional'])
            
            margem = ExpressionWrapper(
                (Value(resultado_operacional) / Value(receita_bruta)) * 100,
                output_field=FloatField()
            ) if receita_bruta > 0 else 0

            # 4. Crescimento
            receita_atual = lancamentos.filter(
                data__year=data_ref.year,
                data__month=data_ref.month,
                tipo='entrada'
            ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')

            receita_anterior = lancamentos.filter(
                data__year=data_ref.year - 1,
                data__month=data_ref.month,
                tipo='entrada'
            ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')

            crescimento = ExpressionWrapper(
                ((Value(receita_atual) - Value(receita_anterior)) / Value(receita_anterior)) * 100,
                output_field=FloatField()
            ) if receita_anterior > 0 else 0

            return {
                'liquidez_imediata': liquidez,
                'ciclo_de_caixa': ciclo_caixa,
                'margem_operacional': margem,
                'crescimento_receita': crescimento
            }

        except Exception as e:
            raise ValueError(f"Erro ao calcular indicadores: {str(e)}")
        
        
    def _obter_saldo_inicial(self, data):
        """Obtém o saldo inicial para uma data"""
        ultimo_saldo = SaldoDiario.objects.filter(
            data__lt=data
        ).order_by('-data').first()
        
        return float(ultimo_saldo.saldo_final if ultimo_saldo else 0)