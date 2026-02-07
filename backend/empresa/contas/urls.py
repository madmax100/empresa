from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.fluxo_caixa.views import FluxoCaixaViewSet
from .views.fluxo_caixa2 import FluxoCaixaViewSet as FluxoCaixaLucroViewSet
from .views.fluxo_caixa_realizado import FluxoCaixaRealizadoViewSet
from .views.analise_fluxo_caixa import AnaliseFluxoCaixaViewSet
from .views.estoque_views import EstoqueViewSet
from .views.produtos_resetados_view import ProdutosResetadosViewSet
from .views.relatorios_views import RelatorioCustosFixosView, RelatorioCustosVariaveisView, RelatorioFaturamentoView
from .views.dre_views import DREView
from .views.access import *
from .views.access import suprimentos_por_contrato
from .views.comparativo_estoque import ComparativoEstoqueView
from .views.compras_views import (
    ComprasResumoView,
    ComprasCadastroView,
    ComprasAtualizarView,
    ComprasContaPagarView,
    ComprasParcelasContaPagarView,
    ComprasBaixaContaPagarView,
    ComprasDetalheView,
    ComprasCancelarNotaView,
    ComprasListaView,
    ComprasCancelarContaPagarView,
)

router = DefaultRouter()
router.register(r'categorias', CategoriasViewSet)
router.register(r'categorias_produtos', CategoriasProdutosViewSet)
router.register(r'clientes', ClientesViewSet)
router.register(r'contagens_inventario', ContagensInventarioViewSet)
router.register(r'contas_pagar', ContasPagarViewSet)
router.register(r'contas_receber', ContasReceberViewSet)
router.register(r'contratos_locacao', ContratosLocacaoViewSet)
router.register(r'custos_adicionais_frete', CustosAdicionaisFreteViewSet)
router.register(r'despesas', DespesasViewSet)
router.register(r'empresas', EmpresasViewSet)
router.register(r'fornecedores', FornecedoresViewSet)
router.register(r'fretes', FretesViewSet)
router.register(r'funcionarios', FuncionariosViewSet)
router.register(r'grupos', GruposViewSet)
router.register(r'historico_rastreamento', HistoricoRastreamentoViewSet)
router.register(r'inventarios', InventariosViewSet)
router.register(r'itens_contrato_locacao', ItensContratoLocacaoViewSet)
router.register(r'itens_nf_entrada', ItensNfEntradaViewSet)
router.register(r'itens_nf_saida', ItensNfSaidaViewSet)
router.register(r'locais_estoque', LocaisEstoqueViewSet)
router.register(r'lotes', LotesViewSet)
router.register(r'marcas', MarcasViewSet)
router.register(r'movimentacoes_estoque', MovimentacoesEstoqueViewSet)
router.register(r'notas_fiscais_entrada', NotasFiscaisEntradaViewSet)
router.register(r'notas_fiscais_saida', NotasFiscaisSaidaViewSet)
router.register(r'ocorrencias_frete', OcorrenciasFreteViewSet)
router.register(r'pagamentos_funcionarios', PagamentosFuncionariosViewSet)
router.register(r'posicoes_estoque', PosicoesEstoqueViewSet)
router.register(r'produtos', ProdutosViewSet)
router.register(r'regioes_entrega', RegioesEntregaViewSet)
router.register(r'saldos_estoque', SaldosEstoqueViewSet)
router.register(r'tabelas_frete', TabelasFreteViewSet)
router.register(r'tipos_movimentacao_estoque', TiposMovimentacaoEstoqueViewSet)
router.register(r'transportadoras', TransportadorasViewSet)
router.register(r'fluxo-caixa', FluxoCaixaViewSet, basename='fluxo-caixa')
router.register(r'fluxo-caixa-lucro', FluxoCaixaLucroViewSet, basename='fluxo-caixa-lucro')
router.register(r'fluxo-caixa-realizado', FluxoCaixaRealizadoViewSet, basename='fluxo-caixa-realizado')
router.register(r'analise-fluxo-caixa', AnaliseFluxoCaixaViewSet, basename='analise-fluxo-caixa')
router.register(r'estoque-controle', EstoqueViewSet, basename='estoque-controle')
router.register(r'produtos-resetados', ProdutosResetadosViewSet, basename='produtos-resetados')


urlpatterns = [
    path('contratos_locacao/suprimentos/', suprimentos_por_contrato, name='suprimentos-por-contrato'),
    path('relatorio-financeiro/', relatorio_financeiro_periodo, name='relatorio-financeiro-periodo'),
    path('relatorio-valor-estoque/', relatorio_valor_estoque, name='relatorio-valor-estoque'),
    path('contas-por-data-pagamento/', contas_por_data_pagamento, name='contas-por-data-pagamento'),
    path('contas-por-data-vencimento/', contas_por_data_vencimento, name='contas-por-data-vencimento'),
    path('contas-nao-pagas-por-data-corte/', contas_nao_pagas_por_data_corte, name='contas-nao-pagas-por-data-corte'),
    
    # Nova rota para o relatório de custos fixos
    path('relatorios/custos-fixos/', RelatorioCustosFixosView.as_view(), name='relatorio-custos-fixos'),
    
    # Nova rota para o relatório de custos variáveis
    path('relatorios/custos-variaveis/', RelatorioCustosVariaveisView.as_view(), name='relatorio-custos-variaveis'),
    
    # Nova rota para o relatório de faturamento
    path('relatorios/faturamento/', RelatorioFaturamentoView.as_view(), name='relatorio-faturamento'),
    
    # DRE - Demonstrativo de Resultados
    path('dre/', DREView.as_view(), name='dre'),
    path('estoque-comparativo/', ComparativoEstoqueView.as_view(), name='estoque-comparativo'),
    path('compras/resumo/', ComprasResumoView.as_view(), name='compras-resumo'),
    path('compras/registrar/', ComprasCadastroView.as_view(), name='compras-registrar'),
    path('compras/atualizar/<int:nota_id>/', ComprasAtualizarView.as_view(), name='compras-atualizar'),
    path('compras/conta-pagar/', ComprasContaPagarView.as_view(), name='compras-conta-pagar'),
    path('compras/conta-pagar/parcelas/', ComprasParcelasContaPagarView.as_view(), name='compras-conta-pagar-parcelas'),
    path('compras/conta-pagar/baixar/', ComprasBaixaContaPagarView.as_view(), name='compras-conta-pagar-baixar'),
    path('compras/detalhe/<int:nota_id>/', ComprasDetalheView.as_view(), name='compras-detalhe'),
    path('compras/cancelar/<int:nota_id>/', ComprasCancelarNotaView.as_view(), name='compras-cancelar'),
    path('compras/', ComprasListaView.as_view(), name='compras-lista'),
    path('compras/conta-pagar/cancelar/', ComprasCancelarContaPagarView.as_view(), name='compras-conta-pagar-cancelar'),
    
    path('', include(router.urls)),
]
