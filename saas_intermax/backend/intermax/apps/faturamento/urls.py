from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.faturamento import views

router = DefaultRouter()
router.register("registros", views.FaturamentoRegistroViewSet, basename="faturamento-registro")
router.register("contratos", views.ContratoSuprimentoViewSet, basename="contrato-suprimento")
router.register("custos-fixos", views.CustoFixoViewSet, basename="custo-fixo")
router.register("custos-variaveis", views.CustoVariavelViewSet, basename="custo-variavel")
router.register("notas", views.NotaFiscalViewSet, basename="nota-fiscal")

urlpatterns = [
    path("resumo/", views.FaturamentoResumoView.as_view(), name="faturamento-resumo"),
    path("contratos/resumo/", views.ContratosResumoView.as_view(), name="contratos-resumo"),
    path("relatorios/faturamento/", views.RelatorioFaturamentoView.as_view(), name="relatorio-faturamento"),
    path("", include(router.urls)),
]
