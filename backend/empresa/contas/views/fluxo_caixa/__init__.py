# empresa/contas/views/fluxo_caixa/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from contas.models import FluxoCaixaLancamento
from contas.serializers.fluxo_caixa import FluxoCaixaLancamentoSerializer
from contas.mixins.fluxo_caixa.analise import FluxoCaixaAnaliseMixin
from contas.mixins.fluxo_caixa.base import FluxoCaixaBaseMixin
from contas.mixins.fluxo_caixa.clientes import ClienteAnalysisMixin
from contas.mixins.fluxo_caixa.conciliacao import FluxoCaixaConciliacaoMixin
from contas.mixins.fluxo_caixa.contratos import ContratosAnalysisMixin
from contas.mixins.fluxo_caixa.dashboard import DashboardMixin
from contas.mixins.fluxo_caixa.dashboardEstrategico import DashboardEstrategicoMixin
from contas.mixins.fluxo_caixa.dre import DREMixin
from contas.mixins.fluxo_caixa.operacoes import FluxoCaixaOperacoesMixin
from contas.mixins.fluxo_caixa.reports import ReportsMixin
from contas.mixins.fluxo_caixa.tendencias import FluxoCaixaTendenciasMixin
from contas.mixins.fluxo_caixa.utils import FluxoCaixaUtilsMixin
from contas.mixins.fluxo_caixa.vendasEstoque import VendasEstoqueMixin


class FluxoCaixaViewSet(FluxoCaixaAnaliseMixin, FluxoCaixaBaseMixin, ClienteAnalysisMixin,
                        FluxoCaixaConciliacaoMixin, ContratosAnalysisMixin, DashboardMixin,
                        DashboardEstrategicoMixin, DREMixin, FluxoCaixaOperacoesMixin,
                        ReportsMixin, FluxoCaixaTendenciasMixin, FluxoCaixaUtilsMixin,
                        VendasEstoqueMixin,
                       viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento do fluxo de caixa
    """
    #queryset = FluxoCaixaLancamento.objects.all()
    #serializer_class = FluxoCaixaLancamentoSerializer
    #permission_classes = [IsAuthenticated]