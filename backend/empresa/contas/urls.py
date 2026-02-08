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
    ComprasContaPagarAgingView,
    ComprasContaPagarAtrasadasView,
    ComprasContaPagarResumoFornecedorView,
    ComprasContaPagarPagasResumoView,
    ComprasContaPagarFluxoView,
    ComprasDevolucaoView,
    ComprasDevolucaoListaView,
    ComprasCancelarDevolucaoView,
    ComprasAtualizarDevolucaoView,
    ComprasDevolucaoSaldoView,
    ComprasDevolucaoResumoView,
    ComprasDevolucaoPorNotaView,
    ComprasRequisicaoCadastrarView,
    ComprasRequisicaoAprovarView,
    ComprasCotacaoCadastrarView,
    ComprasCotacaoAprovarView,
    ComprasPedidoGerarView,
    ComprasPedidoAprovarView,
    ComprasPedidoEnviarView,
    ComprasPedidoCancelarView,
    ComprasPedidoDetalheView,
    ComprasPedidoListaView,
    ComprasParcelasContaPagarView,
    ComprasBaixaContaPagarView,
    ComprasEstornoContaPagarView,
    ComprasDetalheView,
    ComprasCancelarNotaView,
    ComprasListaView,
    ComprasCancelarContaPagarView,
)
from .views.crm_views import (
    CrmAtividadesPendentesView,
    CrmFunilResumoView,
    CrmOportunidadesResumoView,
)
from .views.fiscal_views import (
    FiscalApuracaoGerarView,
    FiscalApuracaoResumoView,
)
from .views.contabilidade_views import (
    BalanceteView,
    CentroCustoViewSet,
    ItemLancamentoContabilViewSet,
    LancamentoContabilViewSet,
    PeriodoContabilViewSet,
    PlanoContasViewSet,
    RazaoContaView,
)
from .views.ativos_views import (
    AtivosDepreciacaoGerarView,
    AtivosResumoView,
    ManutencaoAbrirView,
    ManutencaoCancelarView,
    ManutencaoFinalizarView,
)
from .views.rh_views import (
    RhFolhaFecharView,
    RhFolhaGerarView,
    RhResumoBeneficiosView,
)
from .views.producao_views import (
    ProducaoApontarView,
    ProducaoConsumoApontarView,
    ProducaoOrdemAprovarView,
    ProducaoOrdemCancelarView,
    ProducaoOrdemFinalizarView,
    ProducaoOrdemGerarView,
    ProducaoOrdemIniciarView,
    ProducaoOrdensListaView,
    ProducaoResumoView,
)
from .views.produtos_views import (
    ProdutosAlertasView,
    ProdutosComposicaoResumoView,
    ProdutosConversaoView,
    ProdutosFichaTecnicaView,
    ProdutosHistoricoPrecoView,
    ProdutosPrecoView,
    ProdutosSubstitutosView,
)
from .views.vendas_views import (
    VendasAprovarView,
    VendasCadastroView,
    VendasCancelarView,
    VendasConverterOrcamentoView,
    VendasFaturarView,
    VendasListaView,
    VendasResumoView,
    VendasContaReceberBaixaView,
    VendasContaReceberEstornoView,
    VendasContaReceberAgingView,
    VendasContaReceberAtrasadasView,
    VendasDetalheView,
    VendasAtualizarView,
    VendasEstornoFaturamentoView,
    VendasDevolucaoView,
    VendasDevolucaoListaView,
    VendasDevolucaoCancelarView,
    VendasDevolucaoSaldoView,
    VendasComissaoGerarView,
    VendasComissaoResumoView,
    VendasExpedicaoPendentesView,
    VendasExpedicaoConfirmarView,
    VendasExpedicaoEstornoView,
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
router.register(r'impostos-fiscais', ImpostosFiscaisViewSet)
router.register(r'apuracoes-fiscais', ApuracoesFiscaisViewSet)
router.register(r'itens-apuracao-fiscal', ItensApuracaoFiscalViewSet)
router.register(r'ordens-producao', OrdensProducaoViewSet)
router.register(r'itens-ordem-producao', ItensOrdemProducaoViewSet)
router.register(r'consumos-producao', ConsumosProducaoViewSet)
router.register(r'apontamentos-producao', ApontamentosProducaoViewSet)
router.register(r'ativos-patrimonio', AtivosPatrimonioViewSet)
router.register(r'manutencoes-ativos', ManutencoesAtivosViewSet)
router.register(r'depreciacoes-ativos', DepreciacoesAtivosViewSet)
router.register(r'beneficios-rh', BeneficiosRHViewSet)
router.register(r'vinculos-beneficios-rh', VinculosBeneficiosRHViewSet)
router.register(r'registros-ponto', RegistrosPontoViewSet)
router.register(r'folhas-pagamento', FolhasPagamentoViewSet)
router.register(r'itens-folha-pagamento', ItensFolhaPagamentoViewSet)
router.register(r'admissoes-rh', AdmissoesRHViewSet)
router.register(r'desligamentos-rh', DesligamentosRHViewSet)
router.register(r'etapas-funil', EtapasFunilViewSet)
router.register(r'leads', LeadsViewSet)
router.register(r'oportunidades', OportunidadesViewSet)
router.register(r'atividades-crm', AtividadesCRMViewSet)
router.register(r'propostas-venda', PropostasVendaViewSet)
router.register(r'itens-proposta-venda', ItensPropostaVendaViewSet)
router.register(r'itens_nf_entrada', ItensNfEntradaViewSet)
router.register(r'requisicoes-compra', RequisicoesCompraViewSet)
router.register(r'itens-requisicao-compra', ItensRequisicaoCompraViewSet)
router.register(r'cotacoes-compra', CotacoesCompraViewSet)
router.register(r'itens-cotacao-compra', ItensCotacaoCompraViewSet)
router.register(r'pedidos-compra', PedidosCompraViewSet)
router.register(r'itens-pedido-compra', ItensPedidoCompraViewSet)
router.register(r'itens_nf_saida', ItensNfSaidaViewSet)
router.register(r'orcamentos-venda', OrcamentosVendaViewSet)
router.register(r'itens-orcamento-venda', ItensOrcamentoVendaViewSet)
router.register(r'pedidos-venda', PedidosVendaViewSet)
router.register(r'itens-pedido-venda', ItensPedidoVendaViewSet)
router.register(r'comissoes-venda', ComissoesVendaViewSet)
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
router.register(r'produtos-fiscal', ProdutoFiscalViewSet)
router.register(r'produtos-variacoes', ProdutoVariacaoViewSet)
router.register(r'produtos-composicao', ProdutoComposicaoViewSet)
router.register(r'produtos-conversao-unidade', ProdutoConversaoUnidadeViewSet)
router.register(r'produtos-historico-preco', ProdutoHistoricoPrecoViewSet)
router.register(r'tabelas-precos', TabelaPrecoViewSet)
router.register(r'tabelas-precos-itens', TabelaPrecoItemViewSet)
router.register(r'politicas-desconto', PoliticaDescontoViewSet)
router.register(r'produtos-substitutos', ProdutoSubstitutoViewSet)
router.register(r'produtos-custo-local', ProdutoCustoLocalViewSet)
router.register(r'regioes_entrega', RegioesEntregaViewSet)
router.register(r'saldos_estoque', SaldosEstoqueViewSet)
router.register(r'tabelas_frete', TabelasFreteViewSet)
router.register(r'tipos_movimentacao_estoque', TiposMovimentacaoEstoqueViewSet)
router.register(r'transportadoras', TransportadorasViewSet)
router.register(r'planos-contas', PlanoContasViewSet)
router.register(r'centros-custo', CentroCustoViewSet)
router.register(r'periodos-contabeis', PeriodoContabilViewSet)
router.register(r'lancamentos-contabeis', LancamentoContabilViewSet)
router.register(r'itens-lancamento-contabil', ItemLancamentoContabilViewSet)
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
    path('compras/conta-pagar/aging/', ComprasContaPagarAgingView.as_view(), name='compras-conta-pagar-aging'),
    path('compras/conta-pagar/atrasadas/', ComprasContaPagarAtrasadasView.as_view(), name='compras-conta-pagar-atrasadas'),
    path('compras/conta-pagar/resumo-fornecedor/', ComprasContaPagarResumoFornecedorView.as_view(), name='compras-conta-pagar-resumo-fornecedor'),
    path('compras/conta-pagar/resumo-pagas/', ComprasContaPagarPagasResumoView.as_view(), name='compras-conta-pagar-resumo-pagas'),
    path('compras/conta-pagar/fluxo/', ComprasContaPagarFluxoView.as_view(), name='compras-conta-pagar-fluxo'),
    path('compras/devolucao/', ComprasDevolucaoView.as_view(), name='compras-devolucao'),
    path('compras/devolucao/lista/', ComprasDevolucaoListaView.as_view(), name='compras-devolucao-lista'),
    path('compras/devolucao/cancelar/', ComprasCancelarDevolucaoView.as_view(), name='compras-devolucao-cancelar'),
    path('compras/devolucao/atualizar/', ComprasAtualizarDevolucaoView.as_view(), name='compras-devolucao-atualizar'),
    path('compras/devolucao/saldo/<int:nota_id>/', ComprasDevolucaoSaldoView.as_view(), name='compras-devolucao-saldo'),
    path('compras/devolucao/resumo/', ComprasDevolucaoResumoView.as_view(), name='compras-devolucao-resumo'),
    path('compras/devolucao/notas/', ComprasDevolucaoPorNotaView.as_view(), name='compras-devolucao-notas'),
    path('crm/funil/resumo/', CrmFunilResumoView.as_view(), name='crm-funil-resumo'),
    path('crm/atividades/pendentes/', CrmAtividadesPendentesView.as_view(), name='crm-atividades-pendentes'),
    path('crm/oportunidades/resumo/', CrmOportunidadesResumoView.as_view(), name='crm-oportunidades-resumo'),
    path('fiscal/apuracao/gerar/', FiscalApuracaoGerarView.as_view(), name='fiscal-apuracao-gerar'),
    path('fiscal/apuracao/resumo/', FiscalApuracaoResumoView.as_view(), name='fiscal-apuracao-resumo'),
    path('contabilidade/balancete/', BalanceteView.as_view(), name='contabilidade-balancete'),
    path('contabilidade/razao/<int:conta_id>/', RazaoContaView.as_view(), name='contabilidade-razao'),
    path('producao/ordens/gerar/', ProducaoOrdemGerarView.as_view(), name='producao-ordens-gerar'),
    path('producao/ordens/aprovar/', ProducaoOrdemAprovarView.as_view(), name='producao-ordens-aprovar'),
    path('producao/ordens/iniciar/', ProducaoOrdemIniciarView.as_view(), name='producao-ordens-iniciar'),
    path('producao/ordens/finalizar/', ProducaoOrdemFinalizarView.as_view(), name='producao-ordens-finalizar'),
    path('producao/ordens/cancelar/', ProducaoOrdemCancelarView.as_view(), name='producao-ordens-cancelar'),
    path('producao/ordens/lista/', ProducaoOrdensListaView.as_view(), name='producao-ordens-lista'),
    path('producao/ordens/resumo/', ProducaoResumoView.as_view(), name='producao-ordens-resumo'),
    path('producao/consumo/apontar/', ProducaoConsumoApontarView.as_view(), name='producao-consumo-apontar'),
    path('producao/apontar/', ProducaoApontarView.as_view(), name='producao-apontar'),
    path('ativos/depreciacao/gerar/', AtivosDepreciacaoGerarView.as_view(), name='ativos-depreciacao-gerar'),
    path('ativos/resumo/', AtivosResumoView.as_view(), name='ativos-resumo'),
    path('ativos/manutencao/abrir/', ManutencaoAbrirView.as_view(), name='ativos-manutencao-abrir'),
    path('ativos/manutencao/finalizar/', ManutencaoFinalizarView.as_view(), name='ativos-manutencao-finalizar'),
    path('ativos/manutencao/cancelar/', ManutencaoCancelarView.as_view(), name='ativos-manutencao-cancelar'),
    path('rh/folha/gerar/', RhFolhaGerarView.as_view(), name='rh-folha-gerar'),
    path('rh/folha/fechar/', RhFolhaFecharView.as_view(), name='rh-folha-fechar'),
    path('rh/beneficios/resumo/', RhResumoBeneficiosView.as_view(), name='rh-beneficios-resumo'),
    path('compras/requisicoes/registrar/', ComprasRequisicaoCadastrarView.as_view(), name='compras-requisicoes-registrar'),
    path('compras/requisicoes/aprovar/', ComprasRequisicaoAprovarView.as_view(), name='compras-requisicoes-aprovar'),
    path('compras/cotacoes/registrar/', ComprasCotacaoCadastrarView.as_view(), name='compras-cotacoes-registrar'),
    path('compras/cotacoes/aprovar/', ComprasCotacaoAprovarView.as_view(), name='compras-cotacoes-aprovar'),
    path('compras/pedidos/gerar/', ComprasPedidoGerarView.as_view(), name='compras-pedidos-gerar'),
    path('compras/pedidos/aprovar/', ComprasPedidoAprovarView.as_view(), name='compras-pedidos-aprovar'),
    path('compras/pedidos/enviar/', ComprasPedidoEnviarView.as_view(), name='compras-pedidos-enviar'),
    path('compras/pedidos/cancelar/', ComprasPedidoCancelarView.as_view(), name='compras-pedidos-cancelar'),
    path('compras/pedidos/lista/', ComprasPedidoListaView.as_view(), name='compras-pedidos-lista'),
    path('compras/pedidos/detalhe/<int:pedido_id>/', ComprasPedidoDetalheView.as_view(), name='compras-pedidos-detalhe'),
    path('compras/conta-pagar/parcelas/', ComprasParcelasContaPagarView.as_view(), name='compras-conta-pagar-parcelas'),
    path('compras/conta-pagar/baixar/', ComprasBaixaContaPagarView.as_view(), name='compras-conta-pagar-baixar'),
    path('compras/conta-pagar/estornar/', ComprasEstornoContaPagarView.as_view(), name='compras-conta-pagar-estornar'),
    path('compras/detalhe/<int:nota_id>/', ComprasDetalheView.as_view(), name='compras-detalhe'),
    path('compras/cancelar/<int:nota_id>/', ComprasCancelarNotaView.as_view(), name='compras-cancelar'),
    path('compras/', ComprasListaView.as_view(), name='compras-lista'),
    path('compras/conta-pagar/cancelar/', ComprasCancelarContaPagarView.as_view(), name='compras-conta-pagar-cancelar'),
    path('produtos/preco/', ProdutosPrecoView.as_view(), name='produtos-preco'),
    path('produtos/conversao/', ProdutosConversaoView.as_view(), name='produtos-conversao'),
    path('produtos/composicao/<int:produto_id>/', ProdutosComposicaoResumoView.as_view(), name='produtos-composicao-resumo'),
    path('produtos/alertas/', ProdutosAlertasView.as_view(), name='produtos-alertas'),
    path('produtos/ficha/<int:produto_id>/', ProdutosFichaTecnicaView.as_view(), name='produtos-ficha-tecnica'),
    path('produtos/historico-preco/<int:produto_id>/', ProdutosHistoricoPrecoView.as_view(), name='produtos-historico-preco'),
    path('produtos/substitutos/<int:produto_id>/', ProdutosSubstitutosView.as_view(), name='produtos-substitutos'),
    path('vendas/registrar/', VendasCadastroView.as_view(), name='vendas-registrar'),
    path('vendas/aprovar/', VendasAprovarView.as_view(), name='vendas-aprovar'),
    path('vendas/faturar/', VendasFaturarView.as_view(), name='vendas-faturar'),
    path('vendas/cancelar/', VendasCancelarView.as_view(), name='vendas-cancelar'),
    path('vendas/orcamento/converter/', VendasConverterOrcamentoView.as_view(), name='vendas-orcamento-converter'),
    path('vendas/', VendasListaView.as_view(), name='vendas-lista'),
    path('vendas/resumo/', VendasResumoView.as_view(), name='vendas-resumo'),
    path('vendas/conta-receber/baixar/', VendasContaReceberBaixaView.as_view(), name='vendas-conta-receber-baixar'),
    path('vendas/conta-receber/estornar/', VendasContaReceberEstornoView.as_view(), name='vendas-conta-receber-estornar'),
    path('vendas/conta-receber/aging/', VendasContaReceberAgingView.as_view(), name='vendas-conta-receber-aging'),
    path('vendas/conta-receber/atrasadas/', VendasContaReceberAtrasadasView.as_view(), name='vendas-conta-receber-atrasadas'),
    path('vendas/detalhe/<int:pedido_id>/', VendasDetalheView.as_view(), name='vendas-detalhe'),
    path('vendas/atualizar/<int:pedido_id>/', VendasAtualizarView.as_view(), name='vendas-atualizar'),
    path('vendas/faturamento/estornar/', VendasEstornoFaturamentoView.as_view(), name='vendas-faturamento-estornar'),
    path('vendas/devolucao/', VendasDevolucaoView.as_view(), name='vendas-devolucao'),
    path('vendas/devolucao/lista/', VendasDevolucaoListaView.as_view(), name='vendas-devolucao-lista'),
    path('vendas/devolucao/cancelar/', VendasDevolucaoCancelarView.as_view(), name='vendas-devolucao-cancelar'),
    path('vendas/devolucao/saldo/<int:nota_id>/', VendasDevolucaoSaldoView.as_view(), name='vendas-devolucao-saldo'),
    path('vendas/comissoes/gerar/', VendasComissaoGerarView.as_view(), name='vendas-comissoes-gerar'),
    path('vendas/comissoes/resumo/', VendasComissaoResumoView.as_view(), name='vendas-comissoes-resumo'),
    path('vendas/expedicao/pendentes/', VendasExpedicaoPendentesView.as_view(), name='vendas-expedicao-pendentes'),
    path('vendas/expedicao/confirmar/', VendasExpedicaoConfirmarView.as_view(), name='vendas-expedicao-confirmar'),
    path('vendas/expedicao/estornar/', VendasExpedicaoEstornoView.as_view(), name='vendas-expedicao-estornar'),
    
    path('', include(router.urls)),
]
