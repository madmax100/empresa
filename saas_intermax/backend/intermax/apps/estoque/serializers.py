from rest_framework import serializers

from apps.estoque.models import (
    LocalEstoque,
    MovimentacaoEstoque,
    PosicaoEstoque,
    Produto,
    SaldoEstoque,
    TipoMovimentacaoEstoque,
)


class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = [
            "id",
            "nome",
            "sku",
            "unidade",
            "categoria",
            "estoque_minimo",
            "disponivel_locacao",
            "preco_entrada",
            "ativo",
            "criado_em",
        ]


class MovimentacaoEstoqueSerializer(serializers.ModelSerializer):
    produto = ProdutoSerializer(read_only=True)
    produto_id = serializers.PrimaryKeyRelatedField(
        queryset=Produto.objects.all(), source="produto", write_only=True
    )

    class Meta:
        model = MovimentacaoEstoque
        fields = [
            "id",
            "produto",
            "produto_id",
            "data_movimentacao",
            "tipo",
            "quantidade",
            "custo_unitario",
            "valor_unitario",
            "origem",
            "observacoes",
            "documento_referencia",
            "criado_em",
        ]


class LocalEstoqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalEstoque
        fields = ["id", "nome", "descricao"]


class TipoMovimentacaoEstoqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoMovimentacaoEstoque
        fields = ["id", "codigo", "descricao", "tipo"]


class SaldoEstoqueSerializer(serializers.ModelSerializer):
    produto = ProdutoSerializer(read_only=True)
    produto_id = serializers.PrimaryKeyRelatedField(
        queryset=Produto.objects.all(), source="produto", write_only=True
    )
    local = LocalEstoqueSerializer(read_only=True)
    local_id = serializers.PrimaryKeyRelatedField(
        queryset=LocalEstoque.objects.all(), source="local", write_only=True
    )

    class Meta:
        model = SaldoEstoque
        fields = [
            "id",
            "produto",
            "produto_id",
            "local",
            "local_id",
            "quantidade",
            "quantidade_reservada",
            "custo_medio",
            "ultima_movimentacao",
        ]


class PosicaoEstoqueSerializer(serializers.ModelSerializer):
    local = LocalEstoqueSerializer(read_only=True)
    local_id = serializers.PrimaryKeyRelatedField(
        queryset=LocalEstoque.objects.all(), source="local", write_only=True
    )

    class Meta:
        model = PosicaoEstoque
        fields = ["id", "local", "local_id", "codigo", "descricao"]
