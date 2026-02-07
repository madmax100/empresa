from datetime import date

from django.db.models import Sum
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.contas.models import ContaPagar, ContaReceber, FluxoCaixaLancamento, Fornecedor
from apps.contas.serializers import (
    ContaPagarSerializer,
    ContaReceberSerializer,
    FluxoCaixaLancamentoSerializer,
    FornecedorSerializer,
)


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


class ContasPagarResumoView(APIView):
    def get(self, request):
        total_aberto = (
            ContaPagar.objects.filter(status=ContaPagar.STATUS_ABERTA)
            .aggregate(total=Sum("valor"))["total"]
            or 0
        )
        vencidas = ContaPagar.objects.filter(status=ContaPagar.STATUS_ATRASADA).count()
        proximos = ContaPagar.objects.order_by("data_vencimento")[:5]

        return Response(
            {
                "total_aberto": float(total_aberto),
                "vencidas": vencidas,
                "proximos_vencimentos": ContaPagarSerializer(proximos, many=True).data,
            }
        )


class ContasReceberResumoView(APIView):
    def get(self, request):
        total_aberto = (
            ContaReceber.objects.filter(status=ContaReceber.STATUS_ABERTA)
            .aggregate(total=Sum("valor"))["total"]
            or 0
        )
        vencidas = ContaReceber.objects.filter(status=ContaReceber.STATUS_ATRASADA).count()
        proximos = ContaReceber.objects.order_by("data_vencimento")[:5]

        return Response(
            {
                "total_aberto": float(total_aberto),
                "vencidas": vencidas,
                "proximos_recebimentos": ContaReceberSerializer(proximos, many=True).data,
            }
        )


class FluxoCaixaView(APIView):
    def get(self, request):
        entradas = (
            FluxoCaixaLancamento.objects.filter(tipo=FluxoCaixaLancamento.TIPO_ENTRADA)
            .aggregate(total=Sum("valor"))["total"]
            or 0
        )
        saidas = (
            FluxoCaixaLancamento.objects.filter(tipo=FluxoCaixaLancamento.TIPO_SAIDA)
            .aggregate(total=Sum("valor"))["total"]
            or 0
        )
        saldo = entradas - saidas

        return Response(
            {
                "periodo": None,
                "entradas": float(entradas),
                "saidas": float(saidas),
                "saldo": float(saldo),
                "nota": "Fluxo de caixa baseado nas movimentações cadastradas.",
            }
        )


class RelatorioCustosFixosView(APIView):
    def get(self, request):
        data_inicio = _parse_date(request.query_params.get("data_inicio"))
        data_fim = _parse_date(request.query_params.get("data_fim"))
        if not data_inicio or not data_fim:
            return Response(
                {"erro": "data_inicio e data_fim são obrigatórios."}, status=400
            )

        contas = ContaPagar.objects.filter(
            status=ContaPagar.STATUS_PAGA,
            data_pagamento__range=(data_inicio, data_fim),
            fornecedor__tipo__icontains="FIXO",
        )
        total_pago = contas.aggregate(total=Sum("valor"))["total"] or 0

        return Response(
            {
                "parametros": {
                    "data_inicio": data_inicio,
                    "data_fim": data_fim,
                    "filtro_aplicado": "Fornecedores com tipo FIXO",
                },
                "totais_gerais": {"total_valor_pago": float(total_pago)},
                "total_contas_pagas": contas.count(),
                "contas_pagas": ContaPagarSerializer(contas, many=True).data,
            }
        )


class RelatorioCustosVariaveisView(APIView):
    def get(self, request):
        data_inicio = _parse_date(request.query_params.get("data_inicio"))
        data_fim = _parse_date(request.query_params.get("data_fim"))
        if not data_inicio or not data_fim:
            return Response(
                {"erro": "data_inicio e data_fim são obrigatórios."}, status=400
            )

        contas = ContaPagar.objects.filter(
            status=ContaPagar.STATUS_PAGA,
            data_pagamento__range=(data_inicio, data_fim),
            fornecedor__tipo__icontains="VARIAVEL",
        )
        total_pago = contas.aggregate(total=Sum("valor"))["total"] or 0

        return Response(
            {
                "parametros": {
                    "data_inicio": data_inicio,
                    "data_fim": data_fim,
                    "filtro_aplicado": "Fornecedores com tipo VARIAVEL",
                },
                "totais_gerais": {"total_valor_pago": float(total_pago)},
                "total_contas_pagas": contas.count(),
                "contas_pagas": ContaPagarSerializer(contas, many=True).data,
            }
        )


class FornecedorViewSet(viewsets.ModelViewSet):
    queryset = Fornecedor.objects.all()
    serializer_class = FornecedorSerializer


class ContaPagarViewSet(viewsets.ModelViewSet):
    queryset = ContaPagar.objects.all()
    serializer_class = ContaPagarSerializer


class ContaReceberViewSet(viewsets.ModelViewSet):
    queryset = ContaReceber.objects.all()
    serializer_class = ContaReceberSerializer


class FluxoCaixaLancamentoViewSet(viewsets.ModelViewSet):
    queryset = FluxoCaixaLancamento.objects.all()
    serializer_class = FluxoCaixaLancamentoSerializer
