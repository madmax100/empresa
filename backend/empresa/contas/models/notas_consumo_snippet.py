
class NotasFiscaisConsumo(models.Model):
    id = models.AutoField(primary_key=True)
    numero_nota = models.CharField(max_length=20, null=True, blank=True)
    data_emissao = models.DateTimeField(null=True, blank=True)
    fornecedor = models.ForeignKey('Fornecedores', on_delete=models.PROTECT, related_name='notas_fiscais_consumo', null=True, blank=True)
    valor_produtos = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), null=True, blank=True)
    base_calculo_icms = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), null=True, blank=True)
    valor_desconto = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), null=True, blank=True)
    valor_frete = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), null=True, blank=True)
    modalidade_frete = models.CharField(max_length=50, null=True, blank=True)
    valor_icms = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), null=True, blank=True)
    valor_ipi = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), null=True, blank=True)
    valor_icms_st = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), null=True, blank=True)
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), null=True, blank=True)
    forma_pagamento = models.CharField(max_length=50, null=True, blank=True)
    condicoes_pagamento = models.CharField(max_length=100, null=True, blank=True)
    cfop = models.CharField(max_length=10, null=True, blank=True)
    formulario = models.CharField(max_length=50, null=True, blank=True)
    data_conhecimento = models.DateTimeField(null=True, blank=True)
    data_selo = models.DateTimeField(null=True, blank=True)
    data_entrada = models.DateTimeField(null=True, blank=True)
    tipo_nota = models.CharField(max_length=50, null=True, blank=True)
    chave_nfe = models.CharField(max_length=100, null=True, blank=True)
    serie_nota = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        db_table = 'notas_fiscais_consumo'
        verbose_name = 'Nota Fiscal de Consumo'
        verbose_name_plural = 'Notas Fiscais de Consumo'
        ordering = ['id']

    def __str__(self):
        return f"NF Consumo {self.numero_nota}"
