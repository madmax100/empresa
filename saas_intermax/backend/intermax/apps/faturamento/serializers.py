from rest_framework import serializers

from apps.faturamento.models import (
    ContratoSuprimento,
    CustoFixo,
    CustoVariavel,
    FaturamentoRegistro,
    ItemNotaFiscal,
    NotaFiscal,
)


class FaturamentoRegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaturamentoRegistro
        fields = [
            "id",
            "periodo_inicio",
            "periodo_fim",
            "receita_bruta",
            "receita_liquida",
            "ticket_medio",
            "criado_em",
        ]


class ContratoSuprimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContratoSuprimento
        fields = [
            "id",
            "cliente",
            "data_inicio",
            "data_fim",
            "valor_mensal",
            "status",
            "observacoes",
            "criado_em",
        ]


class CustoFixoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustoFixo
        fields = ["id", "descricao", "centro_custo", "valor_mensal", "criado_em"]


class CustoVariavelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustoVariavel
        fields = [
            "id",
            "descricao",
            "valor",
            "data_referencia",
            "criado_em",
        ]


class ItemNotaFiscalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemNotaFiscal
        fields = ["id", "produto", "quantidade", "valor_unitario"]


class NotaFiscalSerializer(serializers.ModelSerializer):
    itens = ItemNotaFiscalSerializer(many=True, read_only=True)

    class Meta:
        model = NotaFiscal
        fields = [
            "id",
            "numero_nota",
            "data_emissao",
            "tipo",
            "operacao",
            "fornecedor",
            "cliente",
            "valor_produtos",
            "valor_total",
            "impostos",
            "itens",
        ]
