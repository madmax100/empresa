from django.db import models


class PlanoContas(models.Model):
    TIPO_CHOICES = [
        ('ativo', 'Ativo'),
        ('passivo', 'Passivo'),
        ('patrimonio', 'Patrimônio Líquido'),
        ('receita', 'Receita'),
        ('despesa', 'Despesa'),
    ]
    NATUREZA_CHOICES = [
        ('devedora', 'Devedora'),
        ('credora', 'Credora'),
    ]

    codigo = models.CharField(max_length=30, unique=True)
    nome = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    natureza = models.CharField(max_length=20, choices=NATUREZA_CHOICES)
    nivel = models.PositiveSmallIntegerField(default=1)
    conta_pai = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='subcontas',
    )
    ativa = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Plano de Contas'
        verbose_name_plural = 'Plano de Contas'
        ordering = ['codigo']

    def __str__(self) -> str:
        return f'{self.codigo} - {self.nome}'


class CentroCusto(models.Model):
    codigo = models.CharField(max_length=30, unique=True)
    nome = models.CharField(max_length=255)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Centro de Custo'
        verbose_name_plural = 'Centros de Custo'
        ordering = ['codigo']

    def __str__(self) -> str:
        return f'{self.codigo} - {self.nome}'


class PeriodoContabil(models.Model):
    STATUS_CHOICES = [
        ('aberto', 'Aberto'),
        ('fechado', 'Fechado'),
    ]

    ano = models.PositiveSmallIntegerField()
    mes = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='aberto')
    fechado_em = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Período Contábil'
        verbose_name_plural = 'Períodos Contábeis'
        unique_together = ('ano', 'mes')
        ordering = ['-ano', '-mes']

    def __str__(self) -> str:
        return f'{self.mes:02d}/{self.ano}'


class LancamentoContabil(models.Model):
    ORIGEM_CHOICES = [
        ('manual', 'Manual'),
        ('financeiro', 'Financeiro'),
        ('estoque', 'Estoque'),
        ('vendas', 'Vendas'),
        ('compras', 'Compras'),
    ]

    data = models.DateField()
    descricao = models.CharField(max_length=255)
    origem = models.CharField(max_length=20, choices=ORIGEM_CHOICES, default='manual')
    documento_ref = models.CharField(max_length=100, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Lançamento Contábil'
        verbose_name_plural = 'Lançamentos Contábeis'
        ordering = ['-data', '-id']

    def __str__(self) -> str:
        return f'{self.data} - {self.descricao}'


class ItemLancamentoContabil(models.Model):
    TIPO_CHOICES = [
        ('D', 'Débito'),
        ('C', 'Crédito'),
    ]

    lancamento = models.ForeignKey(
        LancamentoContabil,
        on_delete=models.CASCADE,
        related_name='itens',
    )
    conta = models.ForeignKey(PlanoContas, on_delete=models.PROTECT, related_name='itens_lancamento')
    centro_custo = models.ForeignKey(
        CentroCusto,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='itens_lancamento',
    )
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    valor = models.DecimalField(max_digits=15, decimal_places=2)
    historico = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Item de Lançamento Contábil'
        verbose_name_plural = 'Itens de Lançamento Contábil'
        ordering = ['id']

    def __str__(self) -> str:
        return f'{self.conta.codigo} {self.tipo} {self.valor}'
