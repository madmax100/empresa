from django.db import models

from apps.estoque.models import Produto


class FaturamentoRegistro(models.Model):
    periodo_inicio = models.DateField()
    periodo_fim = models.DateField()
    receita_bruta = models.DecimalField(max_digits=12, decimal_places=2)
    receita_liquida = models.DecimalField(max_digits=12, decimal_places=2)
    ticket_medio = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-periodo_inicio", "-id"]


class ContratoSuprimento(models.Model):
    STATUS_ATIVO = "ativo"
    STATUS_EXPIRANDO = "expirando"
    STATUS_PENDENTE = "pendente"

    STATUS_CHOICES = [
        (STATUS_ATIVO, "Ativo"),
        (STATUS_EXPIRANDO, "Expirando"),
        (STATUS_PENDENTE, "Pendente"),
    ]

    cliente = models.CharField(max_length=255)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    valor_mensal = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_ATIVO)
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["data_fim", "id"]


class CustoFixo(models.Model):
    descricao = models.CharField(max_length=255)
    centro_custo = models.CharField(max_length=255)
    valor_mensal = models.DecimalField(max_digits=12, decimal_places=2)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["descricao", "id"]


class CustoVariavel(models.Model):
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    data_referencia = models.DateField()
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data_referencia", "-id"]


class NotaFiscal(models.Model):
    TIPO_ENTRADA = "entrada"
    TIPO_SAIDA = "saida"
    TIPO_SERVICO = "servico"

    TIPO_CHOICES = [
        (TIPO_ENTRADA, "Entrada"),
        (TIPO_SAIDA, "Saída"),
        (TIPO_SERVICO, "Serviço"),
    ]

    numero_nota = models.CharField(max_length=64)
    data_emissao = models.DateField()
    tipo = models.CharField(max_length=16, choices=TIPO_CHOICES)
    operacao = models.CharField(max_length=64)
    fornecedor = models.CharField(max_length=255, blank=True)
    cliente = models.CharField(max_length=255, blank=True)
    valor_produtos = models.DecimalField(max_digits=12, decimal_places=2)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2)
    impostos = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ["-data_emissao", "-id"]


class ItemNotaFiscal(models.Model):
    nota = models.ForeignKey(NotaFiscal, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(Produto, on_delete=models.SET_NULL, null=True)
    quantidade = models.DecimalField(max_digits=12, decimal_places=2)
    valor_unitario = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.nota_id} - {self.produto_id}"
