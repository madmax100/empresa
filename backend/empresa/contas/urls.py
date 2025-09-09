from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.fluxo_caixa.views import FluxoCaixaViewSet
from .views.fluxo_caixa2 import FluxoCaixaViewSet as FluxoCaixaLucroViewSet
from .views.fluxo_caixa_realizado import FluxoCaixaRealizadoViewSet
from .views.analise_fluxo_caixa import AnaliseFluxoCaixaViewSet
from .views.estoque_views import EstoqueViewSet
from .views.relatorios_views import RelatorioCustosFixosView
from .views.access import *
from .views.access import suprimentos_por_contrato

router = DefaultRouter()
router.register(r'categorias', CategoriasViewSet)
# ... (outros registros do router)
router.register(r'transportadoras', TransportadorasViewSet)
router.register(r'fluxo-caixa', FluxoCaixaViewSet, basename='fluxo-caixa')
router.register(r'fluxo-caixa-lucro', FluxoCaixaLucroViewSet, basename='fluxo-caixa-lucro')
router.register(r'fluxo-caixa-realizado', FluxoCaixaRealizadoViewSet, basename='fluxo-caixa-realizado')
router.register(r'analise-fluxo-caixa', AnaliseFluxoCaixaViewSet, basename='analise-fluxo-caixa')
router.register(r'estoque-controle', EstoqueViewSet, basename='estoque-controle')


urlpatterns = [
    path('contratos_locacao/suprimentos/', suprimentos_por_contrato, name='suprimentos-por-contrato'),
    path('relatorio-financeiro/', relatorio_financeiro_periodo, name='relatorio-financeiro-periodo'),
    path('relatorio-valor-estoque/', relatorio_valor_estoque, name='relatorio-valor-estoque'),
    path('contas-por-data-pagamento/', contas_por_data_pagamento, name='contas-por-data-pagamento'),
    path('contas-por-data-vencimento/', contas_por_data_vencimento, name='contas-por-data-vencimento'),
    
    # Nova rota para o relatório de custos fixos
    path('relatorios/custos-fixos/', RelatorioCustosFixosView.as_view(), name='relatorio-custos-fixos'),
    
    path('', include(router.urls)),
]

