from decimal import Decimal
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Dict, Any, List
from django.db.models import Sum, Avg, Count, F, Q, Case, When, DecimalField, Max
from django.db.models.functions import ExtractMonth, ExtractYear, TruncDate
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.response import Response
import pandas as pd
import io

class ReportsMixin:
    """
    Mixin para geração de relatórios detalhados do fluxo de caixa
    """

    @action(detail=False, methods=['GET'])
    def relatorio_fluxo_caixa(self, request):
        """Relatório detalhado do fluxo de caixa"""
        try:
            # Parâmetros
            data_inicial = datetime.strptime(
                request.query_params.get('data_inicial', date.today().strftime('%Y-%m-%d')),
                '%Y-%m-%d'
            ).date()
            data_final = datetime.strptime(
                request.query_params.get('data_final', date.today().strftime('%Y-%m-%d')),
                '%Y-%m-%d'
            ).date()
            formato = request.query_params.get('formato', 'json')

            # Busca lançamentos
            lancamentos = self.get_queryset().filter(
                data__range=[data_inicial, data_final]
            ).select_related('cliente', 'fornecedor')

            # Gera relatório
            relatorio = self._gerar_relatorio_fluxo_caixa(lancamentos, data_inicial, data_final)

            # Formata saída
            if formato == 'csv':
                return self._exportar_csv(relatorio, 'fluxo_caixa')
            elif formato == 'excel':
                return self._exportar_excel(relatorio, 'fluxo_caixa')
            else:
                return Response(relatorio)

        except Exception as e:
            return Response({'error': str(e)}, status=400)

    def _gerar_relatorio_fluxo_caixa(self, lancamentos, data_inicial, data_final):
        """Gera estrutura do relatório de fluxo de caixa com contas a pagar e receber."""
        
        # 1. Separar Contas a Pagar e a Receber
        contas_a_pagar_qs = lancamentos.filter(tipo='saida').order_by('data')
        contas_a_receber_qs = lancamentos.filter(tipo='entrada').order_by('data')

        # 2. Serializar os dados para a resposta JSON
        contas_a_pagar = list(contas_a_pagar_qs.values(
            'id', 'data', 'descricao', 'valor', 'categoria', 
            'fornecedor__nome', 'realizado'
        ))
        contas_a_receber = list(contas_a_receber_qs.values(
            'id', 'data', 'descricao', 'valor', 'categoria', 
            'cliente__nome', 'realizado'
        ))

        # 3. Calcular totais
        totais = lancamentos.aggregate(
            total_entradas=Sum(Case(
                When(tipo='entrada', then='valor'),
                default=Decimal('0.0'),
                output_field=DecimalField()
            )),
            total_saidas=Sum(Case(
                When(tipo='saida', then='valor'),
                default=Decimal('0.0'),
                output_field=DecimalField()
            ))
        )

        # 4. Estruturar a resposta final
        relatorio = {
            'periodo': {
                'data_inicial': data_inicial.strftime('%Y-%m-%d'),
                'data_final': data_final.strftime('%Y-%m-%d'),
            },
            'resumo': {
                'total_a_receber': totais.get('total_entradas') or Decimal('0.00'),
                'total_a_pagar': totais.get('total_saidas') or Decimal('0.00'),
                'saldo_periodo': (totais.get('total_entradas') or 0) - (totais.get('total_saidas') or 0)
            },
            'contas_a_receber': contas_a_receber,
            'contas_a_pagar': contas_a_pagar
        }
        
        return relatorio

    @action(detail=False, methods=['GET'])
    def relatorio_dre(self, request):
        """Demonstrativo de Resultados"""
        try:
            # Parâmetros
            ano = int(request.query_params.get('ano', date.today().year))
            mes = int(request.query_params.get('mes', date.today().month))
            formato = request.query_params.get('formato', 'json')

            # Define período
            data_inicial = date(ano, mes, 1)
            if mes == 12:
                data_final = date(ano + 1, 1, 1) - timedelta(days=1)
            else:
                data_final = date(ano, mes + 1, 1) - timedelta(days=1)

            # Busca lançamentos
            lancamentos = self.get_queryset().filter(
                data__range=[data_inicial, data_final]
            )

            # Gera relatório
            relatorio = self._gerar_relatorio_dre(lancamentos, data_inicial, data_final)

            # Formata saída
            if formato == 'csv':
                return self._exportar_csv(relatorio, 'dre')
            elif formato == 'excel':
                return self._exportar_excel(relatorio, 'dre')
            else:
                return Response(relatorio)

        except Exception as e:
            return Response({'error': str(e)}, status=400)

    def _gerar_relatorio_dre(self, lancamentos, data_inicial, data_final):
        """Gera estrutura do DRE"""
        # Receita Bruta
        receita_bruta = lancamentos.filter(
            tipo='entrada'
        ).aggregate(
            total=Sum('valor')
        )['total'] or Decimal('0')

        # Deduções
        deducoes = receita_bruta * Decimal('0.15')  # 15% de impostos e deduções

        # Receita Líquida
        receita_liquida = receita_bruta - deducoes

        # Custos Operacionais
        custos = lancamentos.filter(
            tipo='saida',
            categoria__in=['suprimentos', 'servicos']
        ).aggregate(
            total=Sum('valor')
        )['total'] or Decimal('0')

        # Despesas Operacionais
        despesas = lancamentos.filter(
            tipo='saida',
            categoria__in=['despesas_operacionais', 'despesas_administrativas']
        ).aggregate(
            total=Sum('valor')
        )['total'] or Decimal('0')

        # Resultado
        resultado = receita_liquida - custos - despesas

        return {
            'periodo': {
                'inicio': data_inicial,
                'fim': data_final
            },
            'receitas': {
                'receita_bruta': float(receita_bruta),
                'deducoes': float(deducoes),
                'receita_liquida': float(receita_liquida)
            },
            'custos_despesas': {
                'custos_operacionais': float(custos),
                'despesas_operacionais': float(despesas),
                'total': float(custos + despesas)
            },
            'resultados': {
                'resultado_operacional': float(resultado),
                'margem_liquida': float(
                    (resultado / receita_bruta * 100)
                    if receita_bruta > 0 else 0
                )
            },
            'analise_categorias': self._analisar_categorias_dre(lancamentos)
        }

    def _analisar_categorias_dre(self, lancamentos):
        """Análise detalhada por categoria para o DRE"""
        return lancamentos.values(
            'categoria'
        ).annotate(
            receitas=Sum(Case(
                When(tipo='entrada', then='valor'),
                default=0,
                output_field=DecimalField()
            )),
            custos=Sum(Case(
                When(tipo='saida', then='valor'),
                default=0,
                output_field=DecimalField()
            ))
        ).order_by('-receitas')

    @action(detail=False, methods=['GET'])
    def relatorio_inadimplencia(self, request):
        """Relatório de inadimplência"""
        try:
            # Parâmetros
            data_base = datetime.strptime(
                request.query_params.get('data_base', date.today().strftime('%Y-%m-%d')),
                '%Y-%m-%d'
            ).date()
            formato = request.query_params.get('formato', 'json')

            # Busca lançamentos atrasados
            lancamentos = self.get_queryset().filter(
                tipo='entrada',
                realizado=False,
                data__lt=data_base
            ).select_related('cliente')

            # Gera relatório
            relatorio = self._gerar_relatorio_inadimplencia(lancamentos, data_base)

            # Formata saída
            if formato == 'csv':
                return self._exportar_csv(relatorio, 'inadimplencia')
            elif formato == 'excel':
                return self._exportar_excel(relatorio, 'inadimplencia')
            else:
                return Response(relatorio)

        except Exception as e:
            return Response({'error': str(e)}, status=400)

    def _gerar_relatorio_inadimplencia(self, lancamentos, data_base):
        """Gera estrutura do relatório de inadimplência"""
        # Agrupa por cliente
        inadimplencia_cliente = lancamentos.values(
            'cliente',
            'cliente__nome'
        ).annotate(
            total_valor=Sum('valor'),
            quantidade=Count('id'),
            maior_atraso=Max(data_base - F('data'))
        ).order_by('-total_valor')

        # Agrupa por faixa de atraso
        faixas_atraso = []
        for faixa in [(0, 30), (31, 60), (61, 90), (91, float('inf'))]:
            total = lancamentos.filter(
                data__lte=data_base - timedelta(days=faixa[0]),
                data__gt=data_base - timedelta(days=faixa[1]) if faixa[1] != float('inf') else date.max
            ).aggregate(
                total=Sum('valor'),
                quantidade=Count('id')
            )
            
            faixas_atraso.append({
                'faixa': f"{faixa[0]}-{faixa[1] if faixa[1] != float('inf') else '+'} dias",
                'total': float(total['total'] or 0),
                'quantidade': total['quantidade']
            })

        return {
            'data_base': data_base,
            'resumo': {
                'total_inadimplencia': float(
                    lancamentos.aggregate(
                        total=Sum('valor')
                    )['total'] or 0
                ),
                'quantidade_titulos': lancamentos.count(),
                'quantidade_clientes': inadimplencia_cliente.count()
            },
            'por_cliente': [{
                'cliente': item['cliente'],
                'nome': item['cliente__nome'],
                'total': float(item['total_valor']),
                'quantidade': item['quantidade'],
                'maior_atraso': item['maior_atraso'].days
            } for item in inadimplencia_cliente],
            'por_faixa_atraso': faixas_atraso
        }

    def _exportar_csv(self, dados, nome_arquivo):
        """Exporta dados para CSV"""
        # Converte dados para DataFrame
        df = pd.DataFrame(dados)
        
        # Gera CSV
        output = io.StringIO()
        df.to_csv(output, index=False)
        
        # Prepara response
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}.csv"'
        return response

    def _exportar_excel(self, dados, nome_arquivo):
        """Exporta dados para Excel"""
        # Converte dados para DataFrame
        df = pd.DataFrame(dados)
        
        # Gera Excel
        output = io.BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        
        # Prepara response
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}.xlsx"'
        return response