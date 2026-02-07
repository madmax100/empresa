from django.db import models


class ContratoLocacao(models.Model):
    cliente = models.CharField(max_length=255)
    inicio = models.DateField()
    fim = models.DateField(blank=True, null=True)
    valorcontrato = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valorpacela = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    numeroparcelas = models.CharField(max_length=16, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-inicio", "id"]

    def __str__(self) -> str:
        return f"Contrato {self.id} - {self.cliente}"


class ItemContratoLocacao(models.Model):
    contrato = models.ForeignKey(
        ContratoLocacao, on_delete=models.CASCADE, related_name="itens"
    )
    descricao = models.CharField(max_length=255)
    quantidade = models.PositiveIntegerField(default=1)
    valor_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self) -> str:
        return f"{self.descricao} ({self.quantidade})"


class SuprimentoNota(models.Model):
    contrato = models.ForeignKey(
        ContratoLocacao, on_delete=models.CASCADE, related_name="suprimentos"
    )
    data = models.DateField()
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    descricao = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-data", "id"]

    def __str__(self) -> str:
        return f"{self.contrato_id} - {self.data}"
