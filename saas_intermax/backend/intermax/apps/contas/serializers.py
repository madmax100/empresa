from rest_framework import serializers

from apps.contas.models import ContaPagar, ContaReceber, FluxoCaixaLancamento, Fornecedor


class FornecedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fornecedor
        fields = ["id", "nome", "tipo", "especificacao"]


class ContaPagarSerializer(serializers.ModelSerializer):
    fornecedor = FornecedorSerializer(read_only=True)
    fornecedor_id = serializers.PrimaryKeyRelatedField(
        queryset=Fornecedor.objects.all(), source="fornecedor", write_only=True, required=False
    )

    class Meta:
        model = ContaPagar
        fields = [
            "id",
            "descricao",
            "fornecedor",
            "fornecedor_id",
            "valor",
            "data_vencimento",
            "data_pagamento",
            "status",
            "criado_em",
        ]


class ContaReceberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContaReceber
        fields = [
            "id",
            "descricao",
            "cliente",
            "valor",
            "data_vencimento",
            "data_recebimento",
            "status",
            "criado_em",
        ]


class FluxoCaixaLancamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FluxoCaixaLancamento
        fields = [
            "id",
            "data_lancamento",
            "tipo",
            "valor",
            "categoria",
            "referencia",
            "criado_em",
        ]
