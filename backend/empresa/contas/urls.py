from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.fluxo_caixa.views import FluxoCaixaViewSet
from .views.access import *
from .views.access import suprimentos_por_contrato

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
router.register(r'itens_nf_compra', ItensNfEntradaViewSet)
router.register(r'itens_nf_venda', ItensNfSaidaViewSet)
router.register(r'locais_estoque', LocaisEstoqueViewSet)
router.register(r'lotes', LotesViewSet)
router.register(r'marcas', MarcasViewSet)
router.register(r'movimentacoes_estoque', MovimentacoesEstoqueViewSet)
router.register(r'notas_fiscais_compra', NotasFiscaisEntradaViewSet)
router.register(r'notas_fiscais_venda', NotasFiscaisSaidaViewSet)
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



urlpatterns = [
    path('contratos_locacao/suprimentos/', suprimentos_por_contrato, name='suprimentos-por-contrato'),
    path('', include(router.urls)),
]
