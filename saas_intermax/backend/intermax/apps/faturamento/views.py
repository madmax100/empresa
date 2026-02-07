from datetime import date

from django.db.models import Avg, Sum
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.faturamento.models import (
    ContratoSuprimento,
    CustoFixo,
    CustoVariavel,
    FaturamentoRegistro,
    ItemNotaFiscal,
    NotaFiscal,
)
from apps.faturamento.serializers import (
    ContratoSuprimentoSerializer,
    CustoFixoSerializer,
    CustoVariavelSerializer,
    FaturamentoRegistroSerializer,
    NotaFiscalSerializer,
)


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


class FaturamentoResumoView(APIView):
    def get(self, request):
        valores = FaturamentoRegistro.objects.aggregate(
            receita_bruta=Sum("receita_bruta"),
            receita_liquida=Sum("receita_liquida"),
            ticket_medio=Avg("ticket_medio"),
        )

        return Response(
            {
                "receita_bruta": float(valores["receita_bruta"] or 0),
                "receita_liquida": float(valores["receita_liquida"] or 0),
                "ticket_medio": float(valores["ticket_medio"] or 0),
                "observacao": "Resumo consolidado por período.",
            }
        )


class ContratosResumoView(APIView):
    def get(self, request):
        ativos = ContratoSuprimento.objects.filter(status=ContratoSuprimento.STATUS_ATIVO).count()
        expirando = ContratoSuprimento.objects.filter(
            status=ContratoSuprimento.STATUS_EXPIRANDO
        ).count()
        pendentes = ContratoSuprimento.objects.filter(
            status=ContratoSuprimento.STATUS_PENDENTE
        ).count()

        return Response(
            {
                "ativos": ativos,
                "expirando": expirando,
                "pendentes": pendentes,
                "nota": "Resumo de contratos sincronizado com a base InterMax.",
            }
        )


class RelatorioFaturamentoView(APIView):
    def get(self, request):
        data_inicio = _parse_date(request.query_params.get("data_inicio"))
        data_fim = _parse_date(request.query_params.get("data_fim"))
        if not data_inicio or not data_fim:
            return Response(
                {"erro": "data_inicio e data_fim são obrigatórios."}, status=400
            )

        notas = NotaFiscal.objects.filter(data_emissao__range=(data_inicio, data_fim))
        entradas = notas.filter(tipo=NotaFiscal.TIPO_ENTRADA)
        saidas = notas.filter(tipo=NotaFiscal.TIPO_SAIDA)
        servicos = notas.filter(tipo=NotaFiscal.TIPO_SERVICO)

        itens_saida = ItemNotaFiscal.objects.filter(nota__in=saidas).select_related("produto")
        valor_preco_entrada = sum(
            (item.produto.preco_entrada if item.produto else 0) * float(item.quantidade)
            for item in itens_saida
        )
        valor_vendas = saidas.aggregate(total=Sum("valor_produtos"))["total"] or 0
        margem_bruta = float(valor_vendas) - float(valor_preco_entrada)
        percentual_margem = (
            (margem_bruta / float(valor_vendas)) * 100 if float(valor_vendas) else 0
        )

        return Response(
            {
                "parametros": {
                    "data_inicio": data_inicio,
                    "data_fim": data_fim,
                },
                "totais_gerais": {
                    "total_quantidade_notas": notas.count(),
                    "total_valor_produtos": float(notas.aggregate(total=Sum("valor_produtos"))["total"] or 0),
                    "total_valor_geral": float(notas.aggregate(total=Sum("valor_total"))["total"] or 0),
                    "total_impostos": float(notas.aggregate(total=Sum("impostos"))["total"] or 0),
                    "analise_vendas": {
                        "valor_vendas": float(valor_vendas),
                        "valor_preco_entrada": float(valor_preco_entrada),
                        "margem_bruta": float(margem_bruta),
                        "percentual_margem": float(percentual_margem),
                        "itens_analisados": itens_saida.count(),
                    },
                },
                "resumo_por_tipo": [
                    {
                        "tipo": "Compras (NF Entrada)",
                        "quantidade_notas": entradas.count(),
                        "valor_produtos": float(entradas.aggregate(total=Sum("valor_produtos"))["total"] or 0),
                        "valor_total": float(entradas.aggregate(total=Sum("valor_total"))["total"] or 0),
                        "impostos": float(entradas.aggregate(total=Sum("impostos"))["total"] or 0),
                    },
                    {
                        "tipo": "Vendas (NF Saída)",
                        "quantidade_notas": saidas.count(),
                        "valor_produtos": float(valor_vendas),
                        "valor_total": float(saidas.aggregate(total=Sum("valor_total"))["total"] or 0),
                        "impostos": float(saidas.aggregate(total=Sum("impostos"))["total"] or 0),
                        "valor_preco_entrada": float(valor_preco_entrada),
                        "margem_bruta": float(margem_bruta),
                        "percentual_margem": float(percentual_margem),
                    },
                    {
                        "tipo": "Serviços (NF Serviço)",
                        "quantidade_notas": servicos.count(),
                        "valor_produtos": float(servicos.aggregate(total=Sum("valor_produtos"))["total"] or 0),
                        "valor_total": float(servicos.aggregate(total=Sum("valor_total"))["total"] or 0),
                        "impostos": float(servicos.aggregate(total=Sum("impostos"))["total"] or 0),
                    },
                ],
                "notas_detalhadas": {
                    "compras": NotaFiscalSerializer(entradas[:10], many=True).data,
                    "vendas": NotaFiscalSerializer(saidas[:10], many=True).data,
                    "servicos": NotaFiscalSerializer(servicos[:10], many=True).data,
                },
            }
        )


class FaturamentoRegistroViewSet(viewsets.ModelViewSet):
    queryset = FaturamentoRegistro.objects.all()
    serializer_class = FaturamentoRegistroSerializer


class ContratoSuprimentoViewSet(viewsets.ModelViewSet):
    queryset = ContratoSuprimento.objects.all()
    serializer_class = ContratoSuprimentoSerializer


class CustoFixoViewSet(viewsets.ModelViewSet):
    queryset = CustoFixo.objects.all()
    serializer_class = CustoFixoSerializer


class CustoVariavelViewSet(viewsets.ModelViewSet):
    queryset = CustoVariavel.objects.all()
    serializer_class = CustoVariavelSerializer


class NotaFiscalViewSet(viewsets.ModelViewSet):
    queryset = NotaFiscal.objects.all()
    serializer_class = NotaFiscalSerializer
