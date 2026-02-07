from django.db import models


class Fornecedor(models.Model):
    TIPO_FIXO = "CUSTO FIXO"
    TIPO_VARIAVEL = "CUSTO VARIAVEL"

    nome = models.CharField(max_length=255)
    tipo = models.CharField(max_length=64, blank=True)
    especificacao = models.CharField(max_length=128, blank=True)

    def __str__(self) -> str:
        return self.nome


class ContaPagar(models.Model):
    STATUS_ABERTA = "aberta"
    STATUS_PAGA = "paga"
    STATUS_ATRASADA = "atrasada"

    STATUS_CHOICES = [
        (STATUS_ABERTA, "Aberta"),
        (STATUS_PAGA, "Paga"),
        (STATUS_ATRASADA, "Atrasada"),
    ]

    descricao = models.CharField(max_length=255)
    fornecedor = models.ForeignKey(
        Fornecedor, on_delete=models.SET_NULL, blank=True, null=True
    )
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    data_vencimento = models.DateField()
    data_pagamento = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_ABERTA)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["data_vencimento", "id"]


class ContaReceber(models.Model):
    STATUS_ABERTA = "aberta"
    STATUS_RECEBIDA = "recebida"
    STATUS_ATRASADA = "atrasada"

    STATUS_CHOICES = [
        (STATUS_ABERTA, "Aberta"),
        (STATUS_RECEBIDA, "Recebida"),
        (STATUS_ATRASADA, "Atrasada"),
    ]

    descricao = models.CharField(max_length=255)
    cliente = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    data_vencimento = models.DateField()
    data_recebimento = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_ABERTA)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["data_vencimento", "id"]


class FluxoCaixaLancamento(models.Model):
    TIPO_ENTRADA = "entrada"
    TIPO_SAIDA = "saida"

    TIPO_CHOICES = [
        (TIPO_ENTRADA, "Entrada"),
        (TIPO_SAIDA, "Saída"),
    ]

    data_lancamento = models.DateField()
    tipo = models.CharField(max_length=16, choices=TIPO_CHOICES)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    categoria = models.CharField(max_length=255)
    referencia = models.CharField(max_length=255, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data_lancamento", "-id"]
