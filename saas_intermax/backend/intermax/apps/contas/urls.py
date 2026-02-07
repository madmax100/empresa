from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.contas import views

router = DefaultRouter()
router.register("fornecedores", views.FornecedorViewSet, basename="fornecedor")
router.register("pagar", views.ContaPagarViewSet, basename="conta-pagar")
router.register("receber", views.ContaReceberViewSet, basename="conta-receber")
router.register("fluxo-caixa", views.FluxoCaixaLancamentoViewSet, basename="fluxo-caixa")

urlpatterns = [
    path("resumo/pagar/", views.ContasPagarResumoView.as_view(), name="contas-pagar-resumo"),
    path("resumo/receber/", views.ContasReceberResumoView.as_view(), name="contas-receber-resumo"),
    path("resumo/fluxo-caixa/", views.FluxoCaixaView.as_view(), name="fluxo-caixa-resumo"),
    path("relatorios/custos-fixos/", views.RelatorioCustosFixosView.as_view(), name="custos-fixos"),
    path("relatorios/custos-variaveis/", views.RelatorioCustosVariaveisView.as_view(), name="custos-variaveis"),
    path("", include(router.urls)),
]
