from decimal import Decimal

from django.db import transaction
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
        fields = ('id', 'lancamento', 'conta', 'centro_custo', 'tipo', 'valor', 'historico')
        extra_kwargs = {
            'lancamento': {'read_only': True},
        }


class LancamentoContabilSerializer(serializers.ModelSerializer):
    itens = ItemLancamentoContabilSerializer(many=True)

    class Meta:
        model = LancamentoContabil
        fields = '__all__'

    def validate_itens(self, itens):
        if len(itens) < 2:
            raise serializers.ValidationError('Informe ao menos dois itens de lançamento.')

        total_debito = Decimal('0')
        total_credito = Decimal('0')

        for item in itens:
            valor = item.get('valor')
            if valor is None or valor <= 0:
                raise serializers.ValidationError('Todos os itens devem ter valor maior que zero.')
            if item.get('tipo') == 'D':
                total_debito += valor
            elif item.get('tipo') == 'C':
                total_credito += valor

        if total_debito != total_credito:
            raise serializers.ValidationError('O lançamento deve estar balanceado entre débitos e créditos.')

        return itens

    def create(self, validated_data):
        itens_data = validated_data.pop('itens', [])
        self.validate_itens(itens_data)

        with transaction.atomic():
            lancamento = LancamentoContabil.objects.create(**validated_data)
            ItemLancamentoContabil.objects.bulk_create(
                [ItemLancamentoContabil(lancamento=lancamento, **item) for item in itens_data]
            )

        return lancamento

    def update(self, instance, validated_data):
        itens_data = validated_data.pop('itens', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if itens_data is not None:
            self.validate_itens(itens_data)
            with transaction.atomic():
                ItemLancamentoContabil.objects.filter(lancamento=instance).delete()
                ItemLancamentoContabil.objects.bulk_create(
                    [ItemLancamentoContabil(lancamento=instance, **item) for item in itens_data]
                )

        return instance
