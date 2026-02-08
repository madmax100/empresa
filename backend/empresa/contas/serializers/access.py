import datetime
from rest_framework import serializers

from ..models.access import *


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorias
        fields = ['id', 'nome']
        
class CategoriasProdutosSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriasProdutos
        fields = '__all__'
        
class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clientes
        fields = ['id', 'nome']


class EtapasFunilSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtapasFunil
        fields = '__all__'


class LeadsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leads
        fields = '__all__'


class OportunidadesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Oportunidades
        fields = '__all__'


class AtividadesCRMSerializer(serializers.ModelSerializer):
    class Meta:
        model = AtividadesCRM
        fields = '__all__'


class PropostasVendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropostasVenda
        fields = '__all__'


class ItensPropostaVendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItensPropostaVenda
        fields = '__all__'

class ImpostosFiscaisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImpostosFiscais
        fields = '__all__'


class ApuracoesFiscaisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApuracoesFiscais
        fields = '__all__'


class ItensApuracaoFiscalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItensApuracaoFiscal
        fields = '__all__'

class OrdensProducaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrdensProducao
        fields = '__all__'


class ItensOrdemProducaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItensOrdemProducao
        fields = '__all__'


class ConsumosProducaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsumosProducao
        fields = '__all__'


class ApontamentosProducaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApontamentosProducao
        fields = '__all__'

class AtivosPatrimonioSerializer(serializers.ModelSerializer):
    class Meta:
        model = AtivosPatrimonio
        fields = '__all__'


class ManutencoesAtivosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManutencoesAtivos
        fields = '__all__'


class DepreciacoesAtivosSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepreciacoesAtivos
        fields = '__all__'

class BeneficiosRHSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiosRH
        fields = '__all__'


class VinculosBeneficiosRHSerializer(serializers.ModelSerializer):
    class Meta:
        model = VinculosBeneficiosRH
        fields = '__all__'


class RegistrosPontoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrosPonto
        fields = '__all__'


class FolhasPagamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FolhasPagamento
        fields = '__all__'


class ItensFolhaPagamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItensFolhaPagamento
        fields = '__all__'


class AdmissoesRHSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissoesRH
        fields = '__all__'


class DesligamentosRHSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesligamentosRH
        fields = '__all__'

class ContratoLocacaoSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer(read_only=True)
    
    class Meta:
        model = ContratosLocacao
        fields = [
            'id', 'cliente', 'contrato', 'tipocontrato', 'renovado',
            'totalmaquinas', 'valorcontrato', 'numeroparcelas',
            'valorpacela', 'data', 'inicio', 'fim'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Garante que valorpacela seja sempre um número decimal válido
        if data['valorpacela'] == '""' or data['valorpacela'] is None:
            data['valorpacela'] = '0.00'
        return data
        
class ContagensInventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContagensInventario
        fields = '__all__'
        
class ContasReceberSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True)

    class Meta:
        model = ContasReceber
        fields = [
            'id', 'data', 'vencimento', 'cliente_nome', 'historico',
            'valor', 'status', 'data_pagamento', 'recebido'
        ]
        depth = 1  # Para incluir os dados do cliente/fornecedor

class ContasPagarSerializer(serializers.ModelSerializer):
    fornecedor_nome = serializers.CharField(source='fornecedor.nome', read_only=True)
    fornecedor_tipo = serializers.CharField(source='fornecedor.tipo', read_only=True)
    fornecedor_especificacao = serializers.CharField(source='fornecedor.especificacao', read_only=True)

    class Meta:
        model = ContasPagar
        fields = [
            'id', 'data', 'vencimento', 'fornecedor_nome', 'fornecedor_tipo', 'fornecedor_especificacao', 'historico', 
            'valor', 'status', 'data_pagamento', 'valor_pago'
        ]
        depth = 1
        
class ContratosLocacaoSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer()
    

    class Meta:
        model = ContratosLocacao
        fields = '__all__'
        
class CustosAdicionaisFreteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustosAdicionaisFrete
        fields = '__all__'
        
class DespesasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Despesas
        fields = '__all__'
        
class EmpresasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresas
        fields = '__all__'
        
class FornecedoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fornecedores
        fields = '__all__'
        
class FretesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fretes
        fields = '__all__'
        
class FuncionariosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funcionarios
        fields = '__all__'
        
class GruposSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grupos
        fields = '__all__'
        
class HistoricoRastreamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoRastreamento
        fields = '__all__'
        
class InventariosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventarios
        fields = '__all__'
        
        
class ItensNfEntradaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItensNfEntrada
        fields = '__all__'


class RequisicoesCompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequisicoesCompra
        fields = '__all__'


class ItensRequisicaoCompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItensRequisicaoCompra
        fields = '__all__'


class CotacoesCompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = CotacoesCompra
        fields = '__all__'


class ItensCotacaoCompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItensCotacaoCompra
        fields = '__all__'


class PedidosCompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = PedidosCompra
        fields = '__all__'


class ItensPedidoCompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItensPedidoCompra
        fields = '__all__'


class OrcamentosVendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrcamentosVenda
        fields = '__all__'


class ItensOrcamentoVendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItensOrcamentoVenda
        fields = '__all__'


class PedidosVendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PedidosVenda
        fields = '__all__'


class ItensPedidoVendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItensPedidoVenda
        fields = '__all__'


class ComissoesVendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComissoesVenda
        fields = '__all__'

        
class LocaisEstoqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocaisEstoque
        fields = '__all__'
        
class LotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lotes
        fields = '__all__'
        
class MarcasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marcas
        fields = '__all__'
        
class MovimentacoesEstoqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimentacoesEstoque
        fields = '__all__'
        
class NotasFiscaisEntradaSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotasFiscaisEntrada
        fields = '__all__'
        
class NotasFiscaisSaidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotasFiscaisSaida
        fields = '__all__'
        
class OcorrenciasFreteSerializer(serializers.ModelSerializer):
    class Meta:
        model = OcorrenciasFrete
        fields = '__all__'
        
class PagamentosFuncionariosSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagamentosFuncionarios
        fields = '__all__'
        
class PosicoesEstoqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = PosicoesEstoque
        fields = '__all__'
        
class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produtos
        fields = '__all__'

    def validate_ean(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError('EAN deve conter apenas dígitos.')
        if value and len(value) not in {8, 12, 13, 14}:
            raise serializers.ValidationError('EAN deve ter 8, 12, 13 ou 14 dígitos.')
        return value

class ProdutoFiscalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProdutoFiscal
        fields = '__all__'

class ProdutoVariacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProdutoVariacao
        fields = '__all__'

class ProdutoComposicaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProdutoComposicao
        fields = '__all__'

class ProdutoConversaoUnidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProdutoConversaoUnidade
        fields = '__all__'

class ProdutoHistoricoPrecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProdutoHistoricoPreco
        fields = '__all__'

class TabelaPrecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TabelaPreco
        fields = '__all__'

class TabelaPrecoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TabelaPrecoItem
        fields = '__all__'

class PoliticaDescontoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoliticaDesconto
        fields = '__all__'

class ProdutoSubstitutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProdutoSubstituto
        fields = '__all__'

class ProdutoCustoLocalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProdutoCustoLocal
        fields = '__all__'

class ItensNfSaidaSerializer(serializers.ModelSerializer):
    produto = ProdutoSerializer(read_only=True)  # Inclui todos os dados do produto

    class Meta:
        model = ItensNfSaida
        fields = '__all__'

class ItemContratoLocacaoSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)

    class Meta:
        model = ItensContratoLocacao
        fields = ['id', 'numeroserie', 'modelo', 'inicio','fim', 'categoria']
        
class RegioesEntregaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegioesEntrega
        fields = '__all__'
        
class SaldosEstoqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaldosEstoque
        fields = '__all__'
        
class TabelasFreteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TabelasFrete
        fields = '__all__'
        
class TiposMovimentacaoEstoqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiposMovimentacaoEstoque
        fields = '__all__'
        
class TransportadorasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transportadoras
        fields = '__all__'
