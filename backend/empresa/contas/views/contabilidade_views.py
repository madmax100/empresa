from django.db.models import Case, DecimalField, F, Sum, Value, When
from django.db.models.functions import Coalesce
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import (
    CentroCusto,
    ItemLancamentoContabil,
    LancamentoContabil,
    PeriodoContabil,
    PlanoContas,
)
from ..serializers import (
    CentroCustoSerializer,
    ItemLancamentoContabilSerializer,
    LancamentoContabilSerializer,
    PeriodoContabilSerializer,
    PlanoContasSerializer,
)


class PlanoContasViewSet(viewsets.ModelViewSet):
    queryset = PlanoContas.objects.all()
    serializer_class = PlanoContasSerializer


class CentroCustoViewSet(viewsets.ModelViewSet):
    queryset = CentroCusto.objects.all()
    serializer_class = CentroCustoSerializer


class PeriodoContabilViewSet(viewsets.ModelViewSet):
    queryset = PeriodoContabil.objects.all()
    serializer_class = PeriodoContabilSerializer


class LancamentoContabilViewSet(viewsets.ModelViewSet):
    queryset = LancamentoContabil.objects.prefetch_related('itens')
    serializer_class = LancamentoContabilSerializer


class ItemLancamentoContabilViewSet(viewsets.ModelViewSet):
    queryset = ItemLancamentoContabil.objects.select_related('conta', 'centro_custo', 'lancamento')
    serializer_class = ItemLancamentoContabilSerializer


class BalanceteView(APIView):
    def get(self, request):
        data_inicio = request.query_params.get('data_inicio')
        data_fim = request.query_params.get('data_fim')

        itens = ItemLancamentoContabil.objects.select_related('conta', 'lancamento')
        if data_inicio:
            itens = itens.filter(lancamento__data__gte=data_inicio)
        if data_fim:
            itens = itens.filter(lancamento__data__lte=data_fim)

        agregados = (
            itens.values('conta_id', 'conta__codigo', 'conta__nome', 'conta__tipo', 'conta__natureza')
            .annotate(
                debitos=Coalesce(
                    Sum(
                        Case(
                            When(tipo='D', then=F('valor')),
                            default=Value(0),
                            output_field=DecimalField(max_digits=15, decimal_places=2),
                        )
                    ),
                    Value(0),
                ),
                creditos=Coalesce(
                    Sum(
                        Case(
                            When(tipo='C', then=F('valor')),
                            default=Value(0),
                            output_field=DecimalField(max_digits=15, decimal_places=2),
                        )
                    ),
                    Value(0),
                ),
            )
            .order_by('conta__codigo')
        )

        resultado = []
        for item in agregados:
            saldo = item['debitos'] - item['creditos']
            resultado.append(
                {
                    'conta_id': item['conta_id'],
                    'codigo': item['conta__codigo'],
                    'nome': item['conta__nome'],
                    'tipo': item['conta__tipo'],
                    'natureza': item['conta__natureza'],
                    'debitos': float(item['debitos']),
                    'creditos': float(item['creditos']),
                    'saldo': float(saldo),
                }
            )

        return Response(
            {
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'total_contas': len(resultado),
                'contas': resultado,
            }
        )


class RazaoContaView(APIView):
    def get(self, request, conta_id: int):
        data_inicio = request.query_params.get('data_inicio')
        data_fim = request.query_params.get('data_fim')

        itens = ItemLancamentoContabil.objects.select_related('lancamento', 'conta', 'centro_custo').filter(
            conta_id=conta_id
        )
        if data_inicio:
            itens = itens.filter(lancamento__data__gte=data_inicio)
        if data_fim:
            itens = itens.filter(lancamento__data__lte=data_fim)

        linhas = [
            {
                'lancamento_id': item.lancamento_id,
                'data': item.lancamento.data,
                'descricao': item.lancamento.descricao,
                'documento_ref': item.lancamento.documento_ref,
                'centro_custo': item.centro_custo.nome if item.centro_custo else None,
                'tipo': item.tipo,
                'valor': float(item.valor),
                'historico': item.historico,
            }
            for item in itens.order_by('lancamento__data', 'id')
        ]

        return Response(
            {
                'conta_id': conta_id,
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'total_lancamentos': len(linhas),
                'lancamentos': linhas,
            }
        )
