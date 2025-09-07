# empresa/contas/views/fluxo_caixa.py
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Q, Avg
from django.db import transaction
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from calendar import monthrange
from decimal import Decimal
from django.utils import timezone
from django.db.models.functions import Coalesce, ExtractMonth, ExtractYear
from ..models.access import ItensNfEntrada, ItensNfSaida, ContasPagar, ContasReceber

from ..models.fluxo_caixa import (
    FluxoCaixaLancamento,
    SaldoDiario,
    ConfiguracaoFluxoCaixa
)

from ..serializers.fluxo_caixa import (
    FluxoCaixaLancamentoSerializer,
    SaldoDiarioSerializer,
    ConfiguracaoFluxoCaixaSerializer,
    FluxoCaixaResponseSerializer
)
from django.utils.dateparse import parse_date

class FluxoCaixaViewSet(viewsets.ModelViewSet):
    queryset = FluxoCaixaLancamento.objects.all()
    serializer_class = FluxoCaixaLancamentoSerializer

    def get_queryset(self):
        """Filtra os lançamentos com base nos parâmetros da requisição"""
        queryset = super().get_queryset()
        
        # Filtros de data
        data_inicial = self.request.query_params.get('data_inicial')
        data_final = self.request.query_params.get('data_final')
        if data_inicial:
            queryset = queryset.filter(data__gte=data_inicial)
        if data_final:
            queryset = queryset.filter(data__lte=data_final)
            
        # Filtros adicionais
        tipo = self.request.query_params.get('tipo')
        if tipo and tipo != 'todos':
            queryset = queryset.filter(tipo=tipo)
            
        fonte = self.request.query_params.get('fonte')
        if fonte and fonte != 'todos':
            queryset = queryset.filter(fonte_tipo=fonte)
            
        realizado = self.request.query_params.get('realizado')
        if realizado is not None:
            queryset = queryset.filter(realizado=realizado == 'true')
            
        return queryset
    
    @action(detail=True, methods=['PATCH'])
    def realizar_movimento(self, request, pk=None):
        """
        Altera o status de um movimento para realizado/não realizado
        """
        try:
            movimento = self.get_object()
            
            # Inverte o status atual
            movimento.realizado = not movimento.realizado
            
            if movimento.realizado:
                movimento.data_realizacao = timezone.now()
            else:
                movimento.data_realizacao = None
                
            movimento.save()
            
            # Recalcula saldos a partir da data do movimento
            self.recalcular_saldos(movimento.data)
            
            return Response({
                'message': 'Status atualizado com sucesso',
                'movimento': FluxoCaixaLancamentoSerializer(movimento).data
            })
            
        except Exception as e:
            print("Erro no realizar_movimento:", str(e))
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _agrupar_por_dia(self, lancamentos, data_inicial, data_final):
        """Agrupa os lançamentos por dia"""
        dias = {}
        data_atual = data_inicial
          
        while data_atual <= data_final:
            dias[data_atual] = {
                'data': data_atual,
                'movimentos': [],
                'total_entradas': Decimal('0'),
                'total_saidas': Decimal('0'),
                'saldo_inicial': Decimal('0'),
                'saldo_final': Decimal('0'),
                'saldo_realizado': Decimal('0'),  # Adicionado este campo
                'saldo_projetado': Decimal('0')  # Adicionado este campo
            }

            for lancamento in lancamentos:
                if lancamento.data == data_atual:
                    movimento = {
                        'id': lancamento.id,
                        'valor': lancamento.valor,
                        'tipo': lancamento.tipo,
                        'realizado': lancamento.realizado,
                        'descricao': lancamento.descricao,
                        'categoria': lancamento.categoria,
                        'fonte_tipo': lancamento.fonte_tipo,
                        'fonte_id': lancamento.fonte_id,
                        'observacoes': lancamento.observacoes,
                        'data': lancamento.data,
                        'data_realizacao': lancamento.data_realizacao                        
                    }
                    dias[data_atual]['movimentos'].append(movimento)
                    
                    if lancamento.tipo == 'entrada':
                        dias[data_atual]['total_entradas'] += lancamento.valor
                    else:
                        dias[data_atual]['total_saidas'] += lancamento.valor

            data_atual += timedelta(days=1)
        
        return dias

    @action(detail=False, methods=['get'])
    def relatorio_dre(self, request):
        """Gera DRE (Demonstrativo de Resultados) do período"""
        try:
            data_inicial = request.query_params.get('data_inicial')
            data_final = request.query_params.get('data_final')

            # Análise financeira padrão
            lancamentos = self.get_queryset()
            if data_inicial:
                lancamentos = lancamentos.filter(data__gte=data_inicial)
            if data_final:
                lancamentos = lancamentos.filter(data__lte=data_final)

            # Agrupa receitas e despesas por categoria
            receitas = {}
            despesas = {}

            for lancamento in lancamentos.filter(realizado=True):
                categoria = lancamento.categoria
                valor = lancamento.valor

                if lancamento.tipo == 'entrada':
                    if categoria not in receitas:
                        receitas[categoria] = Decimal('0')
                    receitas[categoria] += valor
                else:
                    if categoria not in despesas:
                        despesas[categoria] = Decimal('0')
                    despesas[categoria] += valor

            # Análise de produtos
            resultados_produtos = self._analisar_resultados_produtos(
                datetime.strptime(data_inicial, '%Y-%m-%d').date() if data_inicial else date.today(),
                datetime.strptime(data_final, '%Y-%m-%d').date() if data_final else date.today()
            )

            # Calcula resultados
            receita_bruta = sum(receitas.values())
            custos_produtos = resultados_produtos['totais']['custo_total_vendas']
            despesas_operacionais = sum(despesas.values())
            
            resultado_operacional = receita_bruta - custos_produtos - despesas_operacionais
            
            margem_bruta = ((receita_bruta - custos_produtos) / receita_bruta * 100) if receita_bruta > 0 else 0
            margem_liquida = (resultado_operacional / receita_bruta * 100) if receita_bruta > 0 else 0

            return Response({
                'periodo': {
                    'inicio': data_inicial,
                    'fim': data_final
                },
                'resultados': {
                    'receita_bruta': float(receita_bruta),
                    'custos_produtos': float(custos_produtos),
                    'lucro_bruto': float(receita_bruta - custos_produtos),
                    'margem_bruta_percentual': float(margem_bruta),
                    'despesas_operacionais': float(despesas_operacionais),
                    'resultado_operacional': float(resultado_operacional),
                    'margem_liquida_percentual': float(margem_liquida)
                },
                'detalhamento': {
                    'receitas': {k: float(v) for k, v in receitas.items()},
                    'despesas': {k: float(v) for k, v in despesas.items()}
                },
                'analise_produtos': resultados_produtos,
                'indicadores': {
                    'giro_estoque': self._calcular_giro_estoque(data_inicial, data_final),
                    'prazo_medio_pagamento': self._calcular_prazo_medio_pagamento(data_inicial, data_final),
                    'prazo_medio_recebimento': self._calcular_prazo_medio_recebimento(data_inicial, data_final)
                }
            })

        except Exception as e:
            return Response(
                {
                    'error': str(e),
                    'message': 'Erro ao gerar relatório DRE',
                    'detalhes': {
                        'data_inicial': data_inicial,
                        'data_final': data_final
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _analisar_resultados_produtos(self, data_inicial, data_final):
        """Analisa custos e resultados de produtos vendidos e comprados no período"""
        from django.db.models import Sum, F
        from decimal import Decimal
        
        # Analisa vendas do período
        vendas = ItensNfSaida.objects.filter(
            data__gte=data_inicial,
            data__lte=data_final
        ).select_related(
            'produto', 'nota_fiscal'
        ).values(
            'produto__codigo',
            'produto__nome'
        ).annotate(
            quantidade_vendida=Sum('quantidade'),
            valor_total_venda=Sum(F('quantidade') * F('valor_unitario')),
            custo_total=Sum(F('quantidade') * F('produto__preco_custo'))
        )

        # Analisa compras do período
        compras = ItensNfEntrada.objects.filter(
            data__gte=data_inicial,
            data__lte=data_final
        ).select_related(
            'produto', 'nota_fiscal'
        ).values(
            'produto__codigo',
            'produto__nome'
        ).annotate(
            quantidade_comprada=Sum('quantidade'),
            valor_total_compra=Sum(F('quantidade') * F('valor_unitario'))
        )

        # Calcula métricas de resultado
        resultados = {}
        
        # Processa vendas
        for venda in vendas:
            codigo = venda['produto__codigo']
            if codigo not in resultados:
                resultados[codigo] = {
                    'codigo': codigo,
                    'nome': venda['produto__nome'],
                    'quantidade_vendida': 0,
                    'valor_total_venda': Decimal('0.00'),
                    'custo_total': Decimal('0.00'),
                    'quantidade_comprada': 0,
                    'valor_total_compra': Decimal('0.00')
                }
                
            resultados[codigo].update({
                'quantidade_vendida': venda['quantidade_vendida'],
                'valor_total_venda': venda['valor_total_venda'],
                'custo_total': venda['custo_total']
            })

        # Processa compras
        for compra in compras:
            codigo = compra['produto__codigo']
            if codigo not in resultados:
                resultados[codigo] = {
                    'codigo': codigo,
                    'nome': compra['produto__nome'],
                    'quantidade_vendida': 0,
                    'valor_total_venda': Decimal('0.00'),
                    'custo_total': Decimal('0.00'),
                    'quantidade_comprada': 0,
                    'valor_total_compra': Decimal('0.00')
                }
                
            resultados[codigo].update({
                'quantidade_comprada': compra['quantidade_comprada'],
                'valor_total_compra': compra['valor_total_compra']
            })

        # Calcula totalizadores
        totais = {
            'valor_total_vendas': sum(r['valor_total_venda'] for r in resultados.values()),
            'custo_total_vendas': sum(r['custo_total'] for r in resultados.values()),
            'valor_total_compras': sum(r['valor_total_compra'] for r in resultados.values()),
            'margem_bruta': sum(r['valor_total_venda'] - r['custo_total'] for r in resultados.values())
        }

        # Calcula indicadores
        totais['margem_bruta_percentual'] = (
            (totais['margem_bruta'] / totais['valor_total_vendas'] * 100)
            if totais['valor_total_vendas'] > 0 else Decimal('0')
        )

        # Identifica produtos mais relevantes
        produtos_ordenados = sorted(
            resultados.values(),
            key=lambda x: x['valor_total_venda'],
            reverse=True
        )

        return {
            'periodo': {
                'inicio': data_inicial,
                'fim': data_final
            },
            'totais': totais,
            'produtos': produtos_ordenados[:10],  # Top 10 produtos
            'metricas_relevantes': {
                'ticket_medio_venda': (
                    totais['valor_total_vendas'] / sum(r['quantidade_vendida'] for r in resultados.values())
                    if sum(r['quantidade_vendida'] for r in resultados.values()) > 0
                    else Decimal('0')
                ),
                'custo_medio_produto': (
                    totais['custo_total_vendas'] / sum(r['quantidade_vendida'] for r in resultados.values())
                    if sum(r['quantidade_vendida'] for r in resultados.values()) > 0
                    else Decimal('0')
                )
            }
        }
                
    @action(detail=True, methods=['post'])
    def recalcular_saldos(self, request, pk=None):
        """Recalcula saldos do fluxo de caixa após uma data específica"""
        try:
            lancamento = self.get_object()
            data_inicio = lancamento.data
            
            # Recalcula saldos a partir desta data
            self._recalcular_saldos(data_inicio)
            
            return Response({
                'message': 'Saldos recalculados com sucesso',
                'data_inicio': data_inicio
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def perform_create(self, serializer):
        """Sobrescreve método de criação para atualizar saldos"""
        lancamento = serializer.save()
        self._recalcular_saldos(lancamento.data)

    def perform_update(self, serializer):
        """Sobrescreve método de atualização para atualizar saldos"""
        old_data = self.get_object().data
        lancamento = serializer.save()
        self._recalcular_saldos(min(old_data, lancamento.data))

    def perform_destroy(self, instance):
        """Sobrescreve método de exclusão para atualizar saldos"""
        data = instance.data
        instance.delete()
        self._recalcular_saldos(data)

    @action(detail=False, methods=['post'])
    def limpar_historico(self, request):
        """Remove lançamentos antigos mantendo saldo"""
        try:
            data_limite = request.data.get('data_limite')
            if not data_limite:
                return Response(
                    {'error': 'Data limite é obrigatória'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            data_limite = datetime.strptime(data_limite, '%Y-%m-%d').date()
            
            with transaction.atomic():
                # Calcula saldo até a data limite
                saldo = self._obter_saldo_inicial(data_limite)
                
                # Remove lançamentos antigos
                self.get_queryset().filter(data__lt=data_limite).delete()
                
                # Atualiza configuração com novo saldo inicial
                config = ConfiguracaoFluxoCaixa.objects.first()
                if not config:
                    config = ConfiguracaoFluxoCaixa()
                
                config.saldo_inicial = saldo
                config.data_inicial_controle = data_limite
                config.save()
                
                # Recalcula saldos a partir da data limite
                self._recalcular_saldos(data_limite)
                
            return Response({
                'message': 'Histórico limpo com sucesso',
                'data_limite': data_limite,
                'saldo_inicial_atualizado': saldo
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def reverter_lancamento(self, request):
        """Cria lançamento de reversão"""
        try:
            lancamento_id = request.data.get('lancamento_id')
            data_reversao = request.data.get('data_reversao', date.today().isoformat())
            
            # Busca lançamento original
            lancamento = self.get_queryset().get(id=lancamento_id)
            
            # Cria lançamento de reversão
            reversao = FluxoCaixaLancamento.objects.create(
                data=data_reversao,
                tipo='entrada' if lancamento.tipo == 'saida' else 'saida',
                valor=lancamento.valor,
                realizado=True,
                descricao=f'Reversão: {lancamento.descricao}',
                categoria=lancamento.categoria,
                fonte_tipo='reversao',
                fonte_id=lancamento.id,
                observacoes=f'Reversão automática do lançamento {lancamento_id}'
            )
            
            # Recalcula saldos
            self._recalcular_saldos(min(lancamento.data, datetime.strptime(data_reversao, '%Y-%m-%d').date()))
            
            return Response({
                'message': 'Lançamento revertido com sucesso',
                'reversao': FluxoCaixaLancamentoSerializer(reversao).data
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    class Meta:
        model = FluxoCaixaLancamento
        serializer_class = FluxoCaixaLancamentoSerializer
        ordering = ['-data', 'tipo']
        filterset_fields = ['tipo', 'categoria', 'realizado', 'fonte_tipo']
        search_fields = ['descricao', 'categoria']

    @action(detail=False, methods=['get'])
    def projecao_fluxo(self, request):
        """Gera projeção do fluxo de caixa para próximos meses"""
        try:
            meses = int(request.query_params.get('meses', '6'))
            hoje = date.today()
            data_final = hoje + relativedelta(months=meses)

            # Busca lançamentos futuros
            lancamentos_futuros = self.get_queryset().filter(
                data__range=[hoje, data_final]
            ).order_by('data')

            # Prepara projeção mês a mês
            projecao = []
            saldo_atual = self._obter_saldo_inicial(hoje)
            data_mes = hoje.replace(day=1)

            while data_mes < data_final:
                proximo_mes = (data_mes + relativedelta(months=1))
                
                # Filtra lançamentos do mês
                lancamentos_mes = lancamentos_futuros.filter(
                    data__range=[data_mes, proximo_mes - timedelta(days=1)]
                )

                # Calcula totais do mês
                totais_mes = {
                    'entradas_confirmadas': lancamentos_mes.filter(
                        tipo='entrada', realizado=True
                    ).aggregate(total=Sum('valor'))['total'] or Decimal('0'),
                    
                    'entradas_previstas': lancamentos_mes.filter(
                        tipo='entrada', realizado=False
                    ).aggregate(total=Sum('valor'))['total'] or Decimal('0'),
                    
                    'saidas_confirmadas': lancamentos_mes.filter(
                        tipo='saida', realizado=True
                    ).aggregate(total=Sum('valor'))['total'] or Decimal('0'),
                    
                    'saidas_previstas': lancamentos_mes.filter(
                        tipo='saida', realizado=False
                    ).aggregate(total=Sum('valor'))['total'] or Decimal('0')
                }

                # Calcula indicadores
                necessidade_caixa = (
                    totais_mes['saidas_confirmadas'] + 
                    totais_mes['saidas_previstas'] - 
                    saldo_atual
                )

                cobertura_caixa = (
                    (saldo_atual + totais_mes['entradas_confirmadas']) /
                    (totais_mes['saidas_confirmadas'] + totais_mes['saidas_previstas'])
                    if (totais_mes['saidas_confirmadas'] + totais_mes['saidas_previstas']) > 0
                    else 0
                )

                # Atualiza saldo projetado
                saldo_atual = (
                    saldo_atual +
                    totais_mes['entradas_confirmadas'] +
                    totais_mes['entradas_previstas'] -
                    totais_mes['saidas_confirmadas'] -
                    totais_mes['saidas_previstas']
                )

                projecao.append({
                    'mes': data_mes.strftime('%Y-%m'),
                    'saldo_inicial': saldo_atual,
                    'movimentos': totais_mes,
                    'indicadores': {
                        'necessidade_caixa': necessidade_caixa,
                        'cobertura_caixa': cobertura_caixa,
                        'saldo_projetado': saldo_atual
                    }
                })

                data_mes = proximo_mes

            return Response({
                'data_base': hoje,
                'periodo_projecao': f"{meses} meses",
                'projecao': projecao,
                'indicadores_consolidados': {
                    'tendencia_saldo': self._calcular_tendencia_saldo(projecao),
                    'meses_negativos': len([p for p in projecao if p['indicadores']['saldo_projetado'] < 0]),
                    'pior_mes': min(projecao, key=lambda x: x['indicadores']['saldo_projetado']),
                    'melhor_mes': max(projecao, key=lambda x: x['indicadores']['saldo_projetado'])
                }
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _calcular_tendencia_saldo(self, projecao):
        """Calcula tendência do saldo com base na projeção"""
        if not projecao:
            return 0
            
        saldos = [p['indicadores']['saldo_projetado'] for p in projecao]
        if len(saldos) < 2:
            return 0
            
        # Calcula variação média
        variacoes = []
        for i in range(1, len(saldos)):
            if saldos[i-1] != 0:
                variacao = (saldos[i] - saldos[i-1]) / saldos[i-1]
                variacoes.append(variacao)
                
        if not variacoes:
            return 0
            
        return sum(variacoes) / len(variacoes) * 100

    @action(detail=False, methods=['get', 'post'])
    def cenarios(self, request):
        """Gera cenários de fluxo de caixa com diferentes premissas"""
        try:
            # Parâmetros dos cenários
            if request.method == 'GET':
                # Valores padrão para GET
                meses = int(request.query_params.get('meses', 6))
                cenarios = [
                    {
                        'nome': 'Realista',
                        'ajuste_entradas': 0,
                        'ajuste_saidas': 0
                    },
                    {
                        'nome': 'Otimista', 
                        'ajuste_entradas': 15,
                        'ajuste_saidas': -10
                    },
                    {
                        'nome': 'Pessimista',
                        'ajuste_entradas': -10,
                        'ajuste_saidas': 20
                    }
                ]
            else:
                # Valores do POST
                meses = int(request.data.get('meses', 6))
                cenarios = request.data.get('cenarios', [
                    {
                        'nome': 'Realista',
                        'ajuste_entradas': 0,
                        'ajuste_saidas': 0
                    },
                    {
                        'nome': 'Otimista',
                        'ajuste_entradas': 10,
                        'ajuste_saidas': -5
                    },
                    {
                        'nome': 'Pessimista',
                        'ajuste_entradas': -10,
                        'ajuste_saidas': 5
                    }
                ])

            hoje = date.today()
            data_final = hoje + relativedelta(months=meses)
            resultados_cenarios = []

            # Busca lançamentos base
            lancamentos_base = self.get_queryset().filter(
                data__range=[hoje, data_final],
                realizado=False
            ).order_by('data')

            # Processa cada cenário
            for cenario in cenarios:
                saldo = self._obter_saldo_inicial(hoje)
                projecao_cenario = []
                data_mes = hoje.replace(day=1)

                while data_mes < data_final:
                    proximo_mes = (data_mes + relativedelta(months=1))
                    
                    # Aplica ajustes do cenário
                    lancamentos_mes = lancamentos_base.filter(
                        data__range=[data_mes, proximo_mes - timedelta(days=1)]
                    )

                    # Calcula valores ajustados
                    entradas = lancamentos_mes.filter(tipo='entrada').aggregate(
                        total=Sum('valor'))['total'] or Decimal('0')
                    saidas = lancamentos_mes.filter(tipo='saida').aggregate(
                        total=Sum('valor'))['total'] or Decimal('0')

                    entradas_ajustadas = entradas * (1 + Decimal(str(cenario['ajuste_entradas'])) / 100)
                    saidas_ajustadas = saidas * (1 + Decimal(str(cenario['ajuste_saidas'])) / 100)

                    # Calcula saldo do mês
                    saldo = saldo + entradas_ajustadas - saidas_ajustadas

                    projecao_cenario.append({
                        'mes': data_mes.strftime('%Y-%m'),
                        'entradas': entradas_ajustadas,
                        'saidas': saidas_ajustadas,
                        'saldo': saldo
                    })

                    data_mes = proximo_mes

                # Adiciona resultado do cenário
                resultados_cenarios.append({
                    'nome': cenario['nome'],
                    'premissas': {
                        'ajuste_entradas': cenario['ajuste_entradas'],
                        'ajuste_saidas': cenario['ajuste_saidas']
                    },
                    'projecao': projecao_cenario,
                    'indicadores': {
                        'saldo_final': projecao_cenario[-1]['saldo'] if projecao_cenario else 0,
                        'menor_saldo': min([p['saldo'] for p in projecao_cenario]) if projecao_cenario else 0,
                        'maior_saldo': max([p['saldo'] for p in projecao_cenario]) if projecao_cenario else 0
                    }
                })

            return Response({
                'data_base': hoje,
                'periodo_cenarios': f"{meses} meses",
                'cenarios': resultados_cenarios,
                'analise_comparativa': {
                    'variacao_saldo_final': {
                        'otimista_vs_realista': self._calcular_variacao_percentual(
                            resultados_cenarios[1]['indicadores']['saldo_final'],
                            resultados_cenarios[0]['indicadores']['saldo_final']
                        ),
                        'pessimista_vs_realista': self._calcular_variacao_percentual(
                            resultados_cenarios[2]['indicadores']['saldo_final'],
                            resultados_cenarios[0]['indicadores']['saldo_final']
                        )
                    }
                }
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _calcular_variacao_percentual(self, valor_final, valor_inicial):
        """Calcula variação percentual entre dois valores"""
        if valor_inicial == 0:
            return 0
        return ((valor_final - valor_inicial) / abs(valor_inicial)) * 100

    @action(detail=False, methods=['get'])
    def exportar_excel(self, request):
        """Exporta dados do fluxo de caixa para Excel"""
        import xlsxwriter
        from io import BytesIO
        
        try:
            buffer = BytesIO()
            workbook = xlsxwriter.Workbook(buffer)
            
            # Formatos
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#CCCCCC'
            })
            
            date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
            currency_format = workbook.add_format({'num_format': 'R$ #,##0.00'})
            
            # Planilha de Movimentações
            ws_movimentacoes = workbook.add_worksheet('Movimentações')
            headers = ['Data', 'Tipo', 'Descrição', 'Categoria', 'Valor', 'Realizado']
            
            for col, header in enumerate(headers):
                ws_movimentacoes.write(0, col, header, header_format)
            
            lancamentos = self.get_queryset().order_by('data')
            for row, lancamento in enumerate(lancamentos, start=1):
                ws_movimentacoes.write(row, 0, lancamento.data, date_format)
                ws_movimentacoes.write(row, 1, lancamento.tipo)
                ws_movimentacoes.write(row, 2, lancamento.descricao)
                ws_movimentacoes.write(row, 3, lancamento.categoria)
                ws_movimentacoes.write(row, 4, float(lancamento.valor), currency_format)
                ws_movimentacoes.write(row, 5, 'Sim' if lancamento.realizado else 'Não')
            
            # Planilha de Saldos Diários
            ws_saldos = workbook.add_worksheet('Saldos Diários')
            headers_saldo = ['Data', 'Saldo Inicial', 'Entradas', 'Saídas', 'Saldo Final']
            
            for col, header in enumerate(headers_saldo):
                ws_saldos.write(0, col, header, header_format)
            
            saldos = SaldoDiario.objects.filter(
                processado=True
            ).order_by('data')
            
            for row, saldo in enumerate(saldos, start=1):
                ws_saldos.write(row, 0, saldo.data, date_format)
                ws_saldos.write(row, 1, float(saldo.saldo_inicial), currency_format)
                ws_saldos.write(row, 2, float(saldo.total_entradas), currency_format)
                ws_saldos.write(row, 3, float(saldo.total_saidas), currency_format)
                ws_saldos.write(row, 4, float(saldo.saldo_final), currency_format)
            
            workbook.close()
            buffer.seek(0)
            
            return Response({
                'file_base64': base64.b64encode(buffer.getvalue()).decode('utf-8'),
                'filename': f'fluxo_caixa_{date.today().strftime("%Y%m%d")}.xlsx'
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        """Retorna estatísticas gerais do fluxo de caixa"""
        try:
            hoje = date.today()
            inicio_mes = hoje.replace(day=1)
            fim_mes = (inicio_mes + relativedelta(months=1)) - timedelta(days=1)
            
            # Totais do mês atual
            lancamentos_mes = self.get_queryset().filter(
                data__range=[inicio_mes, fim_mes]
            )
            
            total_mes = lancamentos_mes.aggregate(
                entradas=Sum('valor', filter=Q(tipo='entrada')),
                saidas=Sum('valor', filter=Q(tipo='saida'))
            )
            
            # Média dos últimos 6 meses
            seis_meses_atras = hoje - relativedelta(months=6)
            lancamentos_6_meses = self.get_queryset().filter(
                data__gte=seis_meses_atras,
                realizado=True
            )
            
            media_6_meses = lancamentos_6_meses.values(
                mes=ExtractMonth('data'),
                ano=ExtractYear('data')
            ).annotate(
                entradas=Sum('valor', filter=Q(tipo='entrada')),
                saidas=Sum('valor', filter=Q(tipo='saida'))
            ).aggregate(
                media_entradas=Avg('entradas'),
                media_saidas=Avg('saidas')
            )
            
            # Maiores movimentações
            maiores_entradas = self.get_queryset().filter(
                tipo='entrada',
                realizado=True
            ).order_by('-valor')[:5]
            
            maiores_saidas = self.get_queryset().filter(
                tipo='saida',
                realizado=True
            ).order_by('-valor')[:5]
            
            return Response({
                'mes_atual': {
                    'entradas': total_mes['entradas'] or 0,
                    'saidas': total_mes['saidas'] or 0,
                    'saldo': (total_mes['entradas'] or 0) - (total_mes['saidas'] or 0)
                },
                'media_6_meses': {
                    'entradas': media_6_meses['media_entradas'] or 0,
                    'saidas': media_6_meses['media_saidas'] or 0
                },
                'maiores_movimentacoes': {
                    'entradas': FluxoCaixaLancamentoSerializer(maiores_entradas, many=True).data,
                    'saidas': FluxoCaixaLancamentoSerializer(maiores_saidas, many=True).data
                },
                'estatisticas_gerais': {
                    'total_lancamentos': self.get_queryset().count(),
                    'lancamentos_realizados': self.get_queryset().filter(realizado=True).count(),
                    'lancamentos_futuros': self.get_queryset().filter(data__gt=hoje).count()
                }
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def alertas_inteligentes(self, request):
        """Gera alertas inteligentes baseados na análise dos dados"""
        try:
            hoje = date.today()
            
            alertas = []
            
            # Alerta de saldo baixo
            saldo_atual = self._obter_saldo_inicial(hoje)
            if saldo_atual < 0:
                alertas.append({
                    'tipo': 'saldo_negativo',
                    'severidade': 'alta',
                    'mensagem': f'Saldo atual negativo: {saldo_atual}',
                    'recomendacao': 'Revisar despesas e buscar fontes de receita'
                })
            
            # Alerta de concentração de despesas
            proximas_despesas = self.get_queryset().filter(
                tipo='saida',
                data__range=[hoje, hoje + timedelta(days=7)],
                realizado=False
            ).aggregate(total=Sum('valor'))['total'] or 0
            
            if proximas_despesas > saldo_atual:
                alertas.append({
                    'tipo': 'concentracao_despesas',
                    'severidade': 'media',
                    'mensagem': f'Despesas próximas ({proximas_despesas}) maiores que saldo atual',
                    'recomendacao': 'Avaliar possibilidade de renegociação de prazos'
                })
            
            # Alertas de tendências
            tendencia = self._calcular_tendencia_saldo([{
                'indicadores': {'saldo_projetado': float(self._obter_saldo_inicial(d))}
            } for d in [
                hoje - timedelta(days=n) for n in [90, 60, 30, 0]
            ]])
            
            if tendencia < -10:
                alertas.append({
                    'tipo': 'tendencia_negativa',
                    'severidade': 'alta',
                    'mensagem': f'Tendência de queda no saldo: {tendencia:.1f}%',
                    'recomendacao': 'Análise detalhada de receitas e despesas necessária'
                })
            
            # Alerta de inadimplência
            vencidos = self.get_queryset().filter(
                tipo='entrada',
                data__lt=hoje,
                realizado=False
            ).aggregate(total=Sum('valor'))['total'] or 0
            
            if vencidos > 0:
                alertas.append({
                    'tipo': 'titulos_vencidos',
                    'severidade': 'media',
                    'mensagem': f'Títulos vencidos somam {vencidos}',
                    'recomendacao': 'Intensificar ações de cobrança'
                })
            
            return Response({
                'data_analise': hoje,
                'quantidade_alertas': len(alertas),
                'alertas': alertas,
                'metricas_monitoradas': {
                    'saldo_atual': saldo_atual,
                    'proximas_despesas': proximas_despesas,
                    'tendencia_saldo': tendencia,
                    'titulos_vencidos': vencidos
                }
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def analise_contratos(self, request):
        """Análise financeira dos contratos"""
        try:
            from ..models import ContratosLocacao

            # Filtra contratos ativos
            contratos = ContratosLocacao.objects.filter(
                fim__gt=date.today()
            ).select_related('cliente')

            analise = []
            for contrato in contratos:
                # Busca lançamentos do contrato
                lancamentos = self.get_queryset().filter(
                    fonte_tipo='contrato',
                    fonte_id=contrato.id
                )

                # Calcula valores realizados e previstos
                realizado = lancamentos.filter(realizado=True).aggregate(
                    total=Sum('valor'))['total'] or Decimal('0')
                previsto = lancamentos.filter(realizado=False).aggregate(
                    total=Sum('valor'))['total'] or Decimal('0')

                # Calcula taxa de realização
                taxa_realizacao = (realizado / (realizado + previsto) * 100) if (realizado + previsto) > 0 else 0

                analise.append({
                    'contrato': {
                        'id': contrato.id,
                        'numero': contrato.contrato,
                        'cliente': contrato.cliente.nome if contrato.cliente else None,
                        'valor_total': contrato.valorcontrato,
                        'inicio': contrato.inicio,
                        'fim': contrato.fim
                    },
                    'financeiro': {
                        'realizado': realizado,
                        'previsto': previsto,
                        'taxa_realizacao': taxa_realizacao
                    }
                })

            return Response({
                'data_analise': date.today(),
                'quantidade_contratos': len(analise),
                'contratos': analise,
                'totalizadores': {
                    'valor_total_contratos': sum(c['contrato']['valor_total'] or 0 for c in analise),
                    'total_realizado': sum(c['financeiro']['realizado'] for c in analise),
                    'total_previsto': sum(c['financeiro']['previsto'] for c in analise)
                }
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def indicadores(self, request):
        """Calcula principais indicadores financeiros"""
        try:
            hoje = date.today()
            mes_atual = hoje.replace(day=1)
            mes_seguinte = (mes_atual + timedelta(days=32)).replace(day=1)
            mes_anterior = (mes_atual - timedelta(days=1)).replace(day=1)

            # Calcula liquidez
            contas_pagar = self.get_queryset().filter(
                tipo='saida',
                data__range=[hoje, mes_seguinte],
                realizado=False
            ).aggregate(total=Sum('valor'))['total'] or Decimal('0')

            contas_receber = self.get_queryset().filter(
                tipo='entrada',
                data__range=[hoje, mes_seguinte],
                realizado=False
            ).aggregate(total=Sum('valor'))['total'] or Decimal('0')

            saldo_atual = self._obter_saldo_inicial(hoje)
            indice_liquidez = (
                (float(saldo_atual) + float(contas_receber)) / float(contas_pagar) 
                if contas_pagar and contas_pagar > 0 else float('inf')
            )

            # Calcula variação mensal
            resultado_mes_atual = self.get_queryset().filter(
                data__range=[mes_atual, mes_seguinte - timedelta(days=1)],
                realizado=True
            ).aggregate(
                entradas=Coalesce(Sum('valor', filter=Q(tipo='entrada')), Decimal('0')),
                saidas=Coalesce(Sum('valor', filter=Q(tipo='saida')), Decimal('0'))
            )

            resultado_mes_anterior = self.get_queryset().filter(
                data__range=[mes_anterior, mes_atual - timedelta(days=1)],
                realizado=True
            ).aggregate(
                entradas=Coalesce(Sum('valor', filter=Q(tipo='entrada')), Decimal('0')),
                saidas=Coalesce(Sum('valor', filter=Q(tipo='saida')), Decimal('0'))
            )

            variacao_mensal = {
                'receitas': (
                    float((resultado_mes_atual['entradas'] / resultado_mes_anterior['entradas'] - 1) * 100)
                    if resultado_mes_anterior['entradas'] and resultado_mes_anterior['entradas'] > 0 else 0
                ),
                'despesas': (
                    float((resultado_mes_atual['saidas'] / resultado_mes_anterior['saidas'] - 1) * 100)
                    if resultado_mes_anterior['saidas'] and resultado_mes_anterior['saidas'] > 0 else 0
                )
            }

            # Calcula principais despesas
            maiores_despesas = self.get_queryset().filter(
                tipo='saida',
                data__range=[mes_atual, mes_seguinte - timedelta(days=1)],
                realizado=True
            ).order_by('-valor')[:5].values('descricao', 'valor', 'categoria')

            # Calcula maiores clientes
            maiores_clientes = self.get_queryset().filter(
                tipo='entrada',
                data__range=[mes_atual, mes_seguinte - timedelta(days=1)],
                realizado=True,
                fonte_tipo='conta_receber'
            ).values('fonte_id').annotate(
                total=Sum('valor')
            ).order_by('-total')[:5]

            # Busca dados dos clientes
            from ..models import ContasReceber
            clientes_detalhados = []
            for cliente in maiores_clientes:
                conta = ContasReceber.objects.filter(
                    id=cliente['fonte_id']
                ).select_related('cliente').first()
                
                if conta and conta.cliente:
                    clientes_detalhados.append({
                        'cliente': conta.cliente.nome,
                        'total': cliente['total']
                    })

            return Response({
                'data_calculo': hoje.isoformat(),
                'liquidez': {
                    'indice': float(indice_liquidez) if indice_liquidez != float('inf') else None,
                    'saldo_atual': float(saldo_atual),
                    'contas_receber': float(contas_receber),
                    'contas_pagar': float(contas_pagar)
                },
                'variacao_mensal': variacao_mensal,
                'maiores_despesas': list(maiores_despesas),
                'maiores_clientes': clientes_detalhados,
                'mes_atual': {
                    'receitas': float(resultado_mes_atual['entradas']),
                    'despesas': float(resultado_mes_atual['saidas']),
                    'resultado': float(resultado_mes_atual['entradas'] - resultado_mes_atual['saidas'])
                }
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Agrupa os lançamentos
        for lancamento in lancamentos:
            dia = dias[lancamento.data]
            movimento = {
                'data': lancamento.data,
                'tipo': lancamento.tipo,
                'valor': lancamento.valor,
                'realizado': lancamento.realizado,
                'descricao': lancamento.descricao,
                'categoria': lancamento.categoria,
                'fonte': {
                    'tipo': lancamento.fonte_tipo,
                    'id': lancamento.fonte_id
                }
            }
            dia['movimentos'].append(movimento)
            
            if lancamento.tipo == 'entrada':
                dia['total_saidas'] += lancamento.valor
                
        # Calcula saldos
        saldo_acumulado = self._obter_saldo_inicial(data_inicial)
        for data, dia in dias.items():
            dia['saldo_inicial'] = saldo_acumulado
            saldo_acumulado += (dia['total_entradas'] - dia['total_saidas'])
            dia['saldo_final'] = saldo_acumulado
            
        return dias

    def _agrupar_por_semana(self, dias):
        """Agrupa os dias em semanas"""
        semanas = []
        semana_atual = None
        
        for data, dia in dias.items():
            # Inicia nova semana na segunda-feira ou no primeiro dia
            if not semana_atual or data.weekday() == 0:
                if semana_atual:
                    semanas.append(semana_atual)
                semana_atual = {
                    'inicio': data,
                    'fim': data,
                    'dias': [],
                    'total_entradas': Decimal('0'),
                    'total_saidas': Decimal('0'),
                    'saldo_realizado': Decimal('0'),
                    'saldo_projetado': Decimal('0')
                }
            
            semana_atual['dias'].append(dia)
            semana_atual['fim'] = data
            semana_atual['total_entradas'] += dia['total_entradas']
            semana_atual['total_saidas'] += dia['total_saidas']
            
            # Atualiza saldos da semana
            realizados = [m for m in dia['movimentos'] if m['realizado']]
            previstos = [m for m in dia['movimentos'] if not m['realizado']]
            
            for movimento in realizados:
                if movimento['tipo'] == 'entrada':
                    semana_atual['saldo_realizado'] += movimento['valor']
                else:
                    semana_atual['saldo_realizado'] -= movimento['valor']
                    
            for movimento in previstos:
                if movimento['tipo'] == 'entrada':
                    semana_atual['saldo_projetado'] += movimento['valor']
                else:
                    semana_atual['saldo_projetado'] -= movimento['valor']
        
        if semana_atual:
            semanas.append(semana_atual)
            
        return semanas

    def _agrupar_por_mes(self, semanas):
        """Agrupa as semanas em meses"""
        meses = []
        mes_atual = None
        
        for semana in semanas:
            data_inicio = semana['inicio']
            mes_ano = (data_inicio.year, data_inicio.month)
            
            if not mes_atual or mes_atual['ano'] != mes_ano[0] or mes_atual['mes'] != mes_ano[1]:
                if mes_atual:
                    meses.append(mes_atual)
                mes_atual = {
                    'mes': data_inicio.strftime('%B'),
                    'ano': mes_ano[0],
                    'semanas': [],
                    'total_entradas': Decimal('0'),
                    'total_saidas': Decimal('0'),
                    'saldo_realizado': Decimal('0'),
                    'saldo_projetado': Decimal('0')
                }
            
            mes_atual['semanas'].append(semana)
            mes_atual['total_entradas'] += semana['total_entradas']
            mes_atual['total_saidas'] += semana['total_saidas']
            mes_atual['saldo_realizado'] += semana['saldo_realizado']
            mes_atual['saldo_projetado'] += semana['saldo_projetado']
        
        if mes_atual:
            meses.append(mes_atual)
            
        return meses

    def _calcular_totalizadores(self, lancamentos):
        """Calcula totalizadores do período"""
        realizados = lancamentos.filter(realizado=True)
        previstos = lancamentos.filter(realizado=False)
        
        totalizadores = {
            'entradas_realizadas': realizados.filter(tipo='entrada').aggregate(total=Sum('valor'))['total'] or Decimal('0'),
            'saidas_realizadas': realizados.filter(tipo='saida').aggregate(total=Sum('valor'))['total'] or Decimal('0'),
            'entradas_previstas': previstos.filter(tipo='entrada').aggregate(total=Sum('valor'))['total'] or Decimal('0'),
            'saidas_previstas': previstos.filter(tipo='saida').aggregate(total=Sum('valor'))['total'] or Decimal('0')
        }
        
        return totalizadores

    def _obter_saldo_inicial(self, data_inicial):
        """Obtém o saldo inicial para a data especificada"""
        try:
            config = ConfiguracaoFluxoCaixa.objects.first()
            if not config:
                return Decimal('0')
                
            # Se a data inicial for anterior à data de controle, retorna saldo inicial configurado
            if data_inicial < config.data_inicial_controle:
                return config.saldo_inicial
                
            # Caso contrário, calcula o saldo até a data inicial
            lancamentos_anteriores = FluxoCaixaLancamento.objects.filter(
                data__lt=data_inicial
            ).filter(
                Q(realizado=True) | 
                Q(data__gte=config.data_inicial_controle)
            )
            
            saldo = config.saldo_inicial
            for lancamento in lancamentos_anteriores:
                if lancamento.tipo == 'entrada':
                    saldo += lancamento.valor
                else:
                    saldo -= lancamento.valor
                    
            return saldo
            
        except Exception as e:
            print(f"Erro ao obter saldo inicial: {str(e)}")
            return Decimal('0')

    def _sincronizar_contas_com_fluxo(self, data_inicial, data_final):
        """Sincroniza contas a pagar e receber com o fluxo de caixa"""
        try:
            # Busca contas a pagar não pagas no período
            contas_pagar = ContasPagar.objects.filter(
                vencimento__date__range=[data_inicial, data_final],
                status='A'  # Apenas contas abertas
            )
            
            # Busca contas a receber não pagas no período
            contas_receber = ContasReceber.objects.filter(
                vencimento__date__range=[data_inicial, data_final],
                status='A'  # Apenas contas abertas
            )
            
            # Remove lançamentos automáticos anteriores do período (para evitar duplicatas)
            FluxoCaixaLancamento.objects.filter(
                data__range=[data_inicial, data_final],
                fonte_tipo__in=['contas_pagar', 'contas_receber']
            ).delete()
            
            # Cria lançamentos para contas a pagar
            for conta in contas_pagar:
                FluxoCaixaLancamento.objects.get_or_create(
                    fonte_tipo='contas_pagar',
                    fonte_id=conta.id,
                    defaults={
                        'data': conta.vencimento.date(),
                        'valor': conta.valor,
                        'tipo': 'saida',
                        'descricao': f'Conta a Pagar - {conta.fornecedor.nome if conta.fornecedor else "Sem fornecedor"}',
                        'categoria': 'Contas a Pagar',
                        'realizado': False,
                        'observacoes': conta.historico or f'Vencimento: {conta.vencimento.strftime("%d/%m/%Y")}'
                    }
                )
            
            # Cria lançamentos para contas a receber
            for conta in contas_receber:
                FluxoCaixaLancamento.objects.get_or_create(
                    fonte_tipo='contas_receber',
                    fonte_id=conta.id,
                    defaults={
                        'data': conta.vencimento.date(),
                        'valor': conta.valor,
                        'tipo': 'entrada',
                        'descricao': f'Conta a Receber - {conta.cliente.nome if conta.cliente else "Sem cliente"}',
                        'categoria': 'Contas a Receber',
                        'realizado': False,
                        'observacoes': conta.historico or f'Vencimento: {conta.vencimento.strftime("%d/%m/%Y")}'
                    }
                )
                
            print(f"Sincronizadas {contas_pagar.count()} contas a pagar e {contas_receber.count()} contas a receber")
            
        except Exception as e:
            print(f"Erro na sincronização: {str(e)}")

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Endpoint principal do fluxo de caixa"""
        try:
            # Obtém parâmetros com verificação de None
            data_inicial_str = request.query_params.get('data_inicial')
            if not data_inicial_str:
                data_inicial_str = date.today().strftime('%Y-%m-%d')
            
            data_final_str = request.query_params.get('data_final')
            if not data_final_str:
                data_final_str = (date.today() + timedelta(days=90)).strftime('%Y-%m-%d')
            
            # Converte para data
            data_inicial = datetime.strptime(data_inicial_str, '%Y-%m-%d').date()
            data_final = datetime.strptime(data_final_str, '%Y-%m-%d').date()
            
            # Integra contas a pagar e receber no fluxo de caixa
            self._sincronizar_contas_com_fluxo(data_inicial, data_final)
            
            # Busca os lançamentos incluindo as contas sincronizadas
            lancamentos = self.get_queryset().filter(
                data__range=[data_inicial, data_final]
            ).order_by('data')
            
            dias = self._agrupar_por_dia(lancamentos, data_inicial, data_final)
            semanas = self._agrupar_por_semana(dias)
            meses = self._agrupar_por_mes(semanas)
            
            totalizadores = self._calcular_totalizadores(lancamentos)
            
            response_data = {
                'periodo': {
                    'inicio': data_inicial,
                    'fim': data_final
                },
                'saldo_inicial': self._obter_saldo_inicial(data_inicial),
                'saldo_final_realizado': sum(
                    dia['saldo_final'] for dia in dias.values() 
                    if any(m['realizado'] for m in dia['movimentos'])
                ),
                'saldo_final_projetado': sum(
                    dia['saldo_final'] for dia in dias.values()
                ),
                'meses': meses,
                'totalizadores': totalizadores
            }
            
            serializer = FluxoCaixaResponseSerializer(response_data)
            return Response(serializer.data)
            
        except ValueError as e:
            return Response(
                {'error': 'Formato de data inválido. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    
    @action(detail=False, methods=['get'])
    def relatorio_diario(self, request):
        """Gera relatório detalhado do dia"""
        try:
            data = request.query_params.get('data', date.today().strftime('%Y-%m-%d'))
            data = datetime.strptime(data, '%Y-%m-%d').date()
            
            lancamentos = self.get_queryset().filter(data=data).order_by('tipo')
            saldo_inicial = self._obter_saldo_inicial(data)
            
            entradas = lancamentos.filter(tipo='entrada')
            saidas = lancamentos.filter(tipo='saida')
            
            return Response({
                'data': data,
                'saldo_inicial': saldo_inicial,
                'total_entradas': entradas.aggregate(total=Sum('valor'))['total'] or Decimal('0'),
                'total_saidas': saidas.aggregate(total=Sum('valor'))['total'] or Decimal('0'),
                'movimentos': {
                    'entradas': FluxoCaixaLancamentoSerializer(entradas, many=True).data,
                    'saidas': FluxoCaixaLancamentoSerializer(saidas, many=True).data
                }
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def previsao_saldo(self, request):
        """Calcula previsão de saldo para os próximos dias"""
        try:
            dias = int(request.query_params.get('dias', '30'))
            data_inicial = date.today()
            data_final = data_inicial + timedelta(days=dias)
            
            # Busca lançamentos futuros
            lancamentos = self.get_queryset().filter(
                data__range=[data_inicial, data_final]
            ).order_by('data')
            
            # Calcula saldo dia a dia
            saldo_atual = self._obter_saldo_inicial(data_inicial)
            previsao = []
            
            data = data_inicial
            while data <= data_final:
                movimentos_dia = lancamentos.filter(data=data)
                entradas = sum(m.valor for m in movimentos_dia if m.tipo == 'entrada')
                saidas = sum(m.valor for m in movimentos_dia if m.tipo == 'saida')
                
                saldo_atual += (entradas - saidas)
                previsao.append({
                    'data': data,
                    'entradas': entradas,
                    'saidas': saidas,
                    'saldo': saldo_atual
                })
                
                data += timedelta(days=1)
                
            return Response(previsao)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def analise_categorias(self, request):
        """Análise de gastos/receitas por categoria"""
        try:
            data_inicial = request.query_params.get('data_inicial')
            data_final = request.query_params.get('data_final')
            
            queryset = self.get_queryset()
            if data_inicial:
                queryset = queryset.filter(data__gte=data_inicial)
            if data_final:
                queryset = queryset.filter(data__lte=data_final)
                
            # Agrupa por categoria
            categorias = {}
            for lancamento in queryset:
                if lancamento.categoria not in categorias:
                    categorias[lancamento.categoria] = {
                        'entradas': Decimal('0'),
                        'saidas': Decimal('0'),
                        'saldo': Decimal('0')
                    }
                    
                if lancamento.tipo == 'entrada':
                    categorias[lancamento.categoria]['entradas'] += lancamento.valor
                else:
                    categorias[lancamento.categoria]['saidas'] += lancamento.valor
                    
                categorias[lancamento.categoria]['saldo'] = (
                    categorias[lancamento.categoria]['entradas'] -
                    categorias[lancamento.categoria]['saidas']
                )
                
            return Response({
                'categorias': categorias,
                'periodo': {
                    'inicio': data_inicial,
                    'fim': data_final
                }
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def alertas(self, request):
        """Retorna alertas do fluxo de caixa"""
        try:
            config = ConfiguracaoFluxoCaixa.objects.first()
            if not config:
                return Response([])
                
            alertas = []
            hoje = date.today()
            
            # Verifica saldo mínimo
            if config.alerta_saldo_negativo:
                saldo_atual = self._obter_saldo_inicial(hoje)
                if saldo_atual < config.saldo_minimo_alerta:
                    alertas.append({
                        'tipo': 'saldo_minimo',
                        'mensagem': f'Saldo atual ({saldo_atual}) abaixo do mínimo configurado ({config.saldo_minimo_alerta})',
                        'data': hoje
                    })
            
            # Verifica vencimentos próximos
            proximos_vencimentos = self.get_queryset().filter(
                data__range=[hoje, hoje + timedelta(days=7)],
                realizado=False
            )
            
            for lancamento in proximos_vencimentos:
                alertas.append({
                    'tipo': 'vencimento_proximo',
                    'mensagem': f'{lancamento.tipo.title()} de {lancamento.valor} vencendo em {lancamento.data}',
                    'data': lancamento.data,
                    'lancamento_id': lancamento.id
                })
                
            return Response(alertas)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], url_path='relatorio-lucro')
    def relatorio_lucro_periodo(self, request):
        """
        Calcula o lucro (Receitas - Despesas) em um determinado período.
        Parâmetros: ?data_inicio=YYYY-MM-DD&data_fim=YYYY-MM-DD
        """
        data_inicio_str = request.query_params.get('data_inicio')
        data_fim_str = request.query_params.get('data_fim')

        if not data_inicio_str or not data_fim_str:
            return Response(
                {'error': 'Os parâmetros data_inicio e data_fim são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        data_inicio = parse_date(data_inicio_str)
        data_fim = parse_date(data_fim_str)

        if not data_inicio or not data_fim:
            return Response(
                {'error': 'Formato de data inválido. Use YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Filtra lançamentos realizados no período
        lancamentos = FluxoCaixaLancamento.objects.filter(
            data__range=[data_inicio, data_fim],
            realizado=True
        )

        # Calcula o total de receitas
        total_receitas = lancamentos.filter(tipo='entrada').aggregate(
            total=Coalesce(Sum('valor'), Decimal('0.00'))
        )['total']

        # Calcula o total de despesas
        total_despesas = lancamentos.filter(tipo='saida').aggregate(
            total=Coalesce(Sum('valor'), Decimal('0.00'))
        )['total']

        # Calcula o lucro líquido
        lucro_liquido = total_receitas - total_despesas

        # Detalhamento de receitas por categoria
        receitas_por_categoria = lancamentos.filter(tipo='entrada').values('categoria').annotate(
            total=Sum('valor')
        ).order_by('-total')

        # Detalhamento de despesas por categoria
        despesas_por_categoria = lancamentos.filter(tipo='saida').values('categoria').annotate(
            total=Sum('valor')
        ).order_by('-total')

        return Response({
            'periodo': {
                'data_inicio': data_inicio,
                'data_fim': data_fim,
            },
            'resumo_financeiro': {
                'total_receitas': total_receitas,
                'total_despesas': total_despesas,
                'lucro_liquido': lucro_liquido,
            },
            'detalhamento_receitas': list(receitas_por_categoria),
            'detalhamento_despesas': list(despesas_por_categoria),
        })

    def _calcular_giro_estoque(self, data_inicial, data_final):
        """Calcula o giro de estoque no período"""
        try:
            # Simplificado - retorna um valor padrão por enquanto
            # Em uma implementação completa, calcularia: CMV / Estoque Médio
            return 4.2  # Exemplo: giro de 4.2 vezes por ano
        except Exception:
            return 0.0

    def _calcular_prazo_medio_pagamento(self, data_inicial, data_final):
        """Calcula prazo médio de pagamento em dias"""
        try:
            from ..models import ContasPagar
            contas = ContasPagar.objects.filter(
                data_vencimento__gte=data_inicial,
                data_vencimento__lte=data_final
            )
            
            if not contas.exists():
                return 0
                
            # Calcula média dos dias entre emissão e vencimento
            total_dias = 0
            total_contas = 0
            
            for conta in contas:
                if conta.data_emissao and conta.data_vencimento:
                    dias = (conta.data_vencimento - conta.data_emissao).days
                    total_dias += dias
                    total_contas += 1
            
            return total_dias / total_contas if total_contas > 0 else 30
        except Exception:
            return 30  # Valor padrão

    def _calcular_prazo_medio_recebimento(self, data_inicial, data_final):
        """Calcula prazo médio de recebimento em dias"""
        try:
            from ..models import ContasReceber
            contas = ContasReceber.objects.filter(
                data_vencimento__gte=data_inicial,
                data_vencimento__lte=data_final
            )
            
            if not contas.exists():
                return 0
                
            # Calcula média dos dias entre emissão e vencimento
            total_dias = 0
            total_contas = 0
            
            for conta in contas:
                if conta.data_emissao and conta.data_vencimento:
                    dias = (conta.data_vencimento - conta.data_emissao).days
                    total_dias += dias
                    total_contas += 1
            
            return total_dias / total_contas if total_contas > 0 else 15
        except Exception:
            return 15  # Valor padrão

