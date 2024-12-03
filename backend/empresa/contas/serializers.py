import datetime
from rest_framework import serializers

from .models import *

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

class ContratoLocacaoSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer(read_only=True)
    
    class Meta:
        model = ContratosLocacao
        fields = [
            'id', 'cliente', 'contrato', 'tipocontrato', 'renovado',
            'totalmaquinas', 'valorcontrato', 'numeroparcelas',
            'valorpacela', 'data', 'incio', 'fim'
        ]
        
class ContagensInventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContagensInventario
        fields = '__all__'
        
class ContasReceberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContasReceber
        fields = [
            'id', 'cliente', 'historico', 'valor', 
            'vencimento', 'data_pagamento', 'status',
            'valor_total_pago', 'forma_pagamento'
        ]
        depth = 1  # Para incluir os dados do cliente/fornecedor

class ContasPagarSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContasPagar
        fields = [
            'id', 'fornecedor', 'historico', 'valor', 
            'vencimento', 'data_pagamento', 'status',
            'valor_pago', 'forma_pagamento'
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
        fields = ['id', 'nome', 'codigo']

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
        
