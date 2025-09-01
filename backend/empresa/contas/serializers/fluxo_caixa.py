# empresa/contas/serializers/fluxo_caixa.py
from rest_framework import serializers
from django.utils import timezone
from decimal import Decimal
from ..models.fluxo_caixa import FluxoCaixaLancamento, SaldoDiario, ConfiguracaoFluxoCaixa

class FluxoCaixaLancamentoSerializer(serializers.ModelSerializer):
   cliente_nome = serializers.SerializerMethodField()
   fonte_descricao = serializers.SerializerMethodField()

   class Meta:
       model = FluxoCaixaLancamento
       fields = [
           'id', 'data', 'tipo', 'valor', 'realizado', 
           'descricao', 'categoria', 'fonte_tipo', 'fonte_id',
           'data_realizacao', 'data_estorno', 'lancamento_estornado',
           'cliente', 'cliente_nome', 'fonte_descricao',
           'observacoes'
       ]
       read_only_fields = ['data_realizacao', 'data_estorno']

   def get_cliente_nome(self, obj):
       return obj.cliente.nome if obj.cliente else None

   def get_fonte_descricao(self, obj):
       if obj.fonte_tipo == 'conta_receber':
           from ..models import ContasReceber
           try:
               conta = ContasReceber.objects.get(id=obj.fonte_id)
               return f"CR {conta.id} - {conta.cliente.nome if conta.cliente else 'N/A'}"
           except ContasReceber.DoesNotExist:
               return None
       elif obj.fonte_tipo == 'conta_pagar':
           from ..models import ContasPagar
           try:
               conta = ContasPagar.objects.get(id=obj.fonte_id)
               return f"CP {conta.id} - {conta.fornecedor.nome if conta.fornecedor else 'N/A'}"
           except ContasPagar.DoesNotExist:
               return None
       elif obj.fonte_tipo == 'contrato':
           from ..models import ContratosLocacao
           try:
               contrato = ContratosLocacao.objects.get(id=obj.fonte_id)
               return f"Contrato {contrato.contrato} - {contrato.cliente.nome if contrato.cliente else 'N/A'}"
           except ContratosLocacao.DoesNotExist:
               return None
       return None

   def validate(self, data):
       # Validação de datas
       if data.get('data_realizacao') and data['data_realizacao'].date() < data['data']:
           raise serializers.ValidationError('Data de realização não pode ser anterior à data do lançamento')

       # Validação de estorno
       if data.get('data_estorno') and not data.get('lancamento_estornado'):
           raise serializers.ValidationError('Lançamento estornado deve ser informado quando há data de estorno')

       # Validação de valor
       if data.get('valor', 0) <= 0:
           raise serializers.ValidationError('Valor deve ser maior que zero')

       # Validação de lançamentos futuros realizados
       if data.get('realizado') and data['data'] > timezone.now().date():
           raise serializers.ValidationError('Não é possível marcar como realizado um lançamento futuro')

       return data

   def create(self, validated_data):
       if validated_data.get('realizado'):
           validated_data['data_realizacao'] = timezone.now()
       return super().create(validated_data)

   def update(self, instance, validated_data):
       if validated_data.get('realizado') and not instance.realizado:
           validated_data['data_realizacao'] = timezone.now()
       elif not validated_data.get('realizado') and instance.realizado:
           validated_data['data_realizacao'] = None
       return super().update(instance, validated_data)

class SaldoDiarioSerializer(serializers.ModelSerializer):
    """
    Serializer para saldos diários do fluxo de caixa
    """
    class Meta:
        model = SaldoDiario
        fields = [
            'id', 'data', 'saldo_inicial', 'total_entradas', 'total_saidas',
            'saldo_final', 'total_entradas_realizadas', 'total_saidas_realizadas',
            'total_entradas_previstas', 'total_saidas_previstas', 'processado'
        ]
        read_only_fields = [
            'saldo_final', 'total_entradas_realizadas', 'total_saidas_realizadas',
            'total_entradas_previstas', 'total_saidas_previstas', 'processado'
        ]

class ConfiguracaoFluxoCaixaSerializer(serializers.ModelSerializer):
    """
    Serializer para configurações do fluxo de caixa
    """
    class Meta:
        model = ConfiguracaoFluxoCaixa
        fields = [
            'id', 'saldo_inicial', 'data_inicial_controle', 'dias_previsao',
            'categorias', 'considerar_previsoes', 'alerta_saldo_negativo',
            'saldo_minimo_alerta', 'sincronizar_contas', 'sincronizar_contratos'
        ]

class FluxoCaixaMovimentoSerializer(serializers.Serializer):
    """
    Serializer para movimentos agrupados por período
    """
    data = serializers.DateField()
    tipo = serializers.CharField()
    valor = serializers.DecimalField(max_digits=15, decimal_places=2)
    realizado = serializers.BooleanField()
    descricao = serializers.CharField()
    categoria = serializers.CharField()
    fonte_tipo = serializers.CharField()
    fonte_id = serializers.IntegerField()


class FluxoCaixaDiaSerializer(serializers.Serializer):
    """
    Serializer para resumo diário
    """
    data = serializers.DateField()
    saldo_inicial = serializers.DecimalField(max_digits=15, decimal_places=2)
    saldo_final = serializers.DecimalField(max_digits=15, decimal_places=2)
    movimentos = FluxoCaixaMovimentoSerializer(many=True)
    total_entradas = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_saidas = serializers.DecimalField(max_digits=15, decimal_places=2)
    saldo_realizado = serializers.DecimalField(max_digits=15, decimal_places=2)
    saldo_projetado = serializers.DecimalField(max_digits=15, decimal_places=2)

class FluxoCaixaSemanaSerializer(serializers.Serializer):
    """
    Serializer para resumo semanal
    """
    inicio = serializers.DateField()
    fim = serializers.DateField()
    dias = FluxoCaixaDiaSerializer(many=True)
    total_entradas = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_saidas = serializers.DecimalField(max_digits=15, decimal_places=2)
    saldo_realizado = serializers.DecimalField(max_digits=15, decimal_places=2)
    saldo_projetado = serializers.DecimalField(max_digits=15, decimal_places=2)

class FluxoCaixaMesSerializer(serializers.Serializer):
    """
    Serializer para resumo mensal
    """
    mes = serializers.CharField()
    ano = serializers.IntegerField()
    semanas = FluxoCaixaSemanaSerializer(many=True)
    total_entradas = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_saidas = serializers.DecimalField(max_digits=15, decimal_places=2)
    saldo_realizado = serializers.DecimalField(max_digits=15, decimal_places=2)
    saldo_projetado = serializers.DecimalField(max_digits=15, decimal_places=2)

class FluxoCaixaResponseSerializer(serializers.Serializer):
    """
    Serializer para resposta completa do fluxo de caixa
    """
    periodo = serializers.DictField()
    saldo_inicial = serializers.DecimalField(max_digits=15, decimal_places=2)
    saldo_final_realizado = serializers.DecimalField(max_digits=15, decimal_places=2)
    saldo_final_projetado = serializers.DecimalField(max_digits=15, decimal_places=2)
    meses = FluxoCaixaMesSerializer(many=True)
    totalizadores = serializers.DictField()