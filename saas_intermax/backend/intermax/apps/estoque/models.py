from django.db import models


class Produto(models.Model):
    nome = models.CharField(max_length=255)
    sku = models.CharField(max_length=64, unique=True)
    unidade = models.CharField(max_length=16, default="UN")
    categoria = models.CharField(max_length=64, default="OUTROS")
    estoque_minimo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    disponivel_locacao = models.BooleanField(default=False)
    preco_entrada = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.sku} - {self.nome}"


class MovimentacaoEstoque(models.Model):
    TIPO_ENTRADA = "entrada"
    TIPO_SAIDA = "saida"
    TIPO_AJUSTE = "ajuste"

    TIPO_CHOICES = [
        (TIPO_ENTRADA, "Entrada"),
        (TIPO_SAIDA, "Saída"),
        (TIPO_AJUSTE, "Ajuste"),
    ]

    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name="movimentacoes")
    data_movimentacao = models.DateField()
    tipo = models.CharField(max_length=16, choices=TIPO_CHOICES)
    quantidade = models.DecimalField(max_digits=12, decimal_places=2)
    custo_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valor_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    origem = models.CharField(max_length=255, blank=True)
    observacoes = models.TextField(blank=True)
    documento_referencia = models.CharField(max_length=255, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data_movimentacao", "-id"]

    def __str__(self) -> str:
        return f"{self.produto} - {self.tipo} ({self.quantidade})"


class LocalEstoque(models.Model):
    nome = models.CharField(max_length=128)
    descricao = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.nome


class TipoMovimentacaoEstoque(models.Model):
    codigo = models.CharField(max_length=8, unique=True)
    descricao = models.CharField(max_length=128)
    tipo = models.CharField(max_length=1, choices=[("E", "Entrada"), ("S", "Saída")])

    def __str__(self) -> str:
        return f"{self.codigo} - {self.descricao}"


class SaldoEstoque(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name="saldos")
    local = models.ForeignKey(LocalEstoque, on_delete=models.CASCADE, related_name="saldos")
    quantidade = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantidade_reservada = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    custo_medio = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ultima_movimentacao = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ["produto_id"]


class PosicaoEstoque(models.Model):
    local = models.ForeignKey(LocalEstoque, on_delete=models.CASCADE, related_name="posicoes")
    codigo = models.CharField(max_length=64)
    descricao = models.CharField(max_length=255, blank=True)

    def __str__(self) -> str:
        return f"{self.local} - {self.codigo}"
