from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.estoque import views

router = DefaultRouter()
router.register("produtos", views.ProdutoViewSet, basename="produto")
router.register("movimentacoes", views.MovimentacaoEstoqueViewSet, basename="movimentacao-estoque")
router.register("tipos-movimentacao", views.TipoMovimentacaoEstoqueViewSet, basename="tipo-movimentacao")
router.register("locais", views.LocalEstoqueViewSet, basename="local-estoque")
router.register("saldos", views.SaldoEstoqueViewSet, basename="saldo-estoque")
router.register("posicoes", views.PosicaoEstoqueViewSet, basename="posicao-estoque")

urlpatterns = [
    path("resumo/", views.ResumoEstoqueView.as_view(), name="resumo-estoque"),
    path("relatorio-valor-estoque/", views.RelatorioValorEstoqueView.as_view(), name="relatorio-valor-estoque"),
    path(
        "estoque-controle/movimentacoes_periodo/",
        views.MovimentacoesPeriodoView.as_view(),
        name="movimentacoes-periodo",
    ),
    path("", include(router.urls)),
]
