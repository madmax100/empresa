from rest_framework import serializers
from .models import *

class CategoriasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorias
        fields = '__all__'
        
class CategoriasProdutosSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriasProdutos
        fields = '__all__'
        
class ClientesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clientes
        fields = '__all__'
        
class ContagensInventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContagensInventario
        fields = '__all__'
        
class ContasPagarSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContasPagar
        fields = '__all__'
        
class ContasReceberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContasReceber
        fields = '__all__'
        
class ContratosLocacaoSerializer(serializers.ModelSerializer):
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
        
class ItensContratoLocacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItensContratoLocacao
        fields = '__all__'
        
class ItensNfCompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItensNfCompra
        fields = '__all__'
        
class ItensNfVendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItensNfVenda
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
        
class NotasFiscaisCompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotasFiscaisCompra
        fields = '__all__'
        
class NotasFiscaisVendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotasFiscaisVenda
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
        
class ProdutosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produtos
        fields = '__all__'
        
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
        
