from datetime import date

from django.db.models import Q, Sum
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.locacao.models import ContratoLocacao, SuprimentoNota
from apps.locacao.serializers import ContratoLocacaoSerializer, SuprimentoNotaSerializer


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


class ContratoLocacaoViewSet(viewsets.ModelViewSet):
    queryset = ContratoLocacao.objects.all()
    serializer_class = ContratoLocacaoSerializer


class SuprimentosPorContratoView(APIView):
    def get(self, request):
        data_inicial = _parse_date(request.query_params.get("data_inicial"))
        data_final = _parse_date(request.query_params.get("data_final"))

        if not data_inicial or not data_final:
            return Response(
                {"erro": "data_inicial e data_final são obrigatórios."}, status=400
            )

        contratos = ContratoLocacao.objects.filter(
            Q(inicio__lte=data_final) & (Q(fim__gte=data_inicial) | Q(fim__isnull=True))
        )

        contrato_id = request.query_params.get("contrato_id")
        if contrato_id:
            contratos = contratos.filter(id=contrato_id)

        cliente_id = request.query_params.get("cliente_id")
        if cliente_id:
            contratos = contratos.filter(cliente=cliente_id)

        resultados = []
        total_suprimentos = 0
        contratos_com_atividade = 0

        for contrato in contratos:
            notas = contrato.suprimentos.filter(data__range=(data_inicial, data_final))
            total_valor = notas.aggregate(total=Sum("valor"))["total"] or 0
            quantidade_notas = notas.count()
            if quantidade_notas:
                contratos_com_atividade += 1

            total_suprimentos += total_valor

            resultados.append(
                {
                    "contrato_id": contrato.id,
                    "cliente": contrato.cliente,
                    "vigencia": {
                        "inicio": contrato.inicio,
                        "fim": contrato.fim,
                        "ativo_no_periodo": True,
                    },
                    "valores_contratuais": {
                        "valor_mensal": float(contrato.valorpacela or 0),
                        "valor_total_contrato": float(contrato.valorcontrato or 0),
                        "numero_parcelas": contrato.numeroparcelas,
                    },
                    "suprimentos": {
                        "total_valor": float(total_valor),
                        "quantidade_notas": quantidade_notas,
                        "notas": SuprimentoNotaSerializer(notas, many=True).data,
                    },
                }
            )

        return Response(
            {
                "filtros_aplicados": {
                    "data_inicial": data_inicial,
                    "data_final": data_final,
                    "vigencia_considerada": True,
                },
                "resumo": {
                    "total_contratos_vigentes": contratos.count(),
                    "contratos_com_atividade": contratos_com_atividade,
                    "total_suprimentos": float(total_suprimentos),
                },
                "resultados": resultados,
            }
        )
