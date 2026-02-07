from rest_framework.response import Response
from rest_framework.views import APIView

from apps.contas.models import ContaPagar, ContaReceber
from apps.estoque.models import MovimentacaoEstoque, Produto
from apps.faturamento.models import ContratoSuprimento, FaturamentoRegistro, NotaFiscal
from apps.locacao.models import ContratoLocacao


class HealthCheckView(APIView):
    def get(self, request):
        return Response({"status": "ok"})


class RoadmapView(APIView):
    def get(self, request):
        return Response(
            {
                "modulos": {
                    "estoque": {
                        "produtos": Produto.objects.count(),
                        "movimentacoes": MovimentacaoEstoque.objects.count(),
                    },
                    "contas": {
                        "pagar": ContaPagar.objects.count(),
                        "receber": ContaReceber.objects.count(),
                    },
                    "faturamento": {
                        "registros": FaturamentoRegistro.objects.count(),
                        "contratos": ContratoSuprimento.objects.count(),
                        "notas": NotaFiscal.objects.count(),
                    },
                    "locacao": {
                        "contratos": ContratoLocacao.objects.count(),
                    },
                },
                "pendencias": [
                    "importacao_intermax",
                    "validacao_dados",
                    "painel_kpis",
                ],
                "notes": "Estrutura pronta para integração com dados InterMax.03.02.2026.",
            }
        )
