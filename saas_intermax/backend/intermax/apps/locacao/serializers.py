from rest_framework import serializers

from apps.locacao.models import ContratoLocacao, ItemContratoLocacao, SuprimentoNota


class ItemContratoLocacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemContratoLocacao
        fields = ["id", "descricao", "quantidade", "valor_unitario"]


class ContratoLocacaoSerializer(serializers.ModelSerializer):
    itens = ItemContratoLocacaoSerializer(many=True, read_only=True)

    class Meta:
        model = ContratoLocacao
        fields = [
            "id",
            "cliente",
            "inicio",
            "fim",
            "valorcontrato",
            "valorpacela",
            "numeroparcelas",
            "itens",
        ]


class SuprimentoNotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuprimentoNota
        fields = ["id", "data", "valor", "descricao"]
