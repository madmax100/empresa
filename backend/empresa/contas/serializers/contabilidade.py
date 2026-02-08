from rest_framework import serializers

from ..models import (
    CentroCusto,
    ItemLancamentoContabil,
    LancamentoContabil,
    PeriodoContabil,
    PlanoContas,
)


class PlanoContasSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanoContas
        fields = '__all__'


class CentroCustoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CentroCusto
        fields = '__all__'


class PeriodoContabilSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodoContabil
        fields = '__all__'


class ItemLancamentoContabilSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemLancamentoContabil
        fields = '__all__'


class LancamentoContabilSerializer(serializers.ModelSerializer):
    itens = ItemLancamentoContabilSerializer(many=True, read_only=True)

    class Meta:
        model = LancamentoContabil
        fields = '__all__'
