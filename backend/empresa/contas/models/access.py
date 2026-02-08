import datetime
from django.db import models
from decimal import Decimal

class ContasBancarias(models.Model):
    banco = models.CharField(
        max_length=20,
        verbose_name='Código do Banco',
        db_index=True
    )
    nome_banco = models.CharField(
        max_length=100,
        verbose_name='Nome do Banco'
    )
    numero = models.CharField(
        max_length=20,
        verbose_name='Número da Conta'
    )
    agencia = models.CharField(
        max_length=20,
        verbose_name='Agência'
    )
    contato = models.CharField(
        max_length=100,
        verbose_name='Contato',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'contas_bancarias'
        verbose_name = 'Conta Bancária'
        verbose_name_plural = 'Contas Bancárias'
        ordering = ['nome_banco', 'agencia', 'numero']
        indexes = [
            models.Index(fields=['banco']),
            models.Index(fields=['agencia', 'numero'])
        ]

    def __str__(self):
        return f"{self.nome_banco} - Ag: {self.agencia} CC: {self.numero}"

class Categorias(models.Model):
    codigo = models.IntegerField()
    nome = models.CharField(max_length=50)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    ativo = models.BooleanField(null=True, blank=True, default=True)

    class Meta:
        db_table = 'categorias'

    def __str__(self):
        return str(self.nome)

class CategoriasProdutos(models.Model):
    nome = models.CharField(max_length=50)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    ativo = models.BooleanField(null=True, blank=True, default=True)

    class Meta:
        db_table = 'categorias_produtos'

    def __str__(self):
        return str(self.nome)

class Clientes(models.Model):
    tipo_pessoa = models.CharField(max_length=255, null=True, blank=True, default='F')
    nome = models.CharField(max_length=100)
    cpf_cnpj = models.CharField(max_length=20,null=True, blank=True)
    rg_ie = models.CharField(max_length=20, null=True, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    endereco = models.CharField(max_length=100, null=True, blank=True)
    numero = models.CharField(max_length=10, null=True, blank=True)
    complemento = models.CharField(max_length=50, null=True, blank=True)
    bairro = models.CharField(max_length=50, null=True, blank=True)
    cidade = models.CharField(max_length=50, null=True, blank=True)
    estado = models.CharField(max_length=2, null=True, blank=True)
    cep = models.CharField(max_length=25, null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    limite_credito = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.0)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    ativo = models.BooleanField(null=True, blank=True, default=True)
    contato = models.CharField(max_length=50, null=True, blank=True)
    especificacao = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'clientes'

    def __str__(self):
        return str(self.nome)


class EtapasFunil(models.Model):
    nome = models.CharField(max_length=100)
    ordem = models.IntegerField(default=0)
    ativo = models.BooleanField(default=True)

    class Meta:
        db_table = 'etapas_funil'
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome


class Leads(models.Model):
    STATUS_CHOICES = [
        ('N', 'Novo'),
        ('C', 'Contactado'),
        ('Q', 'Qualificado'),
        ('D', 'Descartado'),
    ]

    nome = models.CharField(max_length=100)
    email = models.CharField(max_length=100, null=True, blank=True)
    telefone = models.CharField(max_length=30, null=True, blank=True)
    origem = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='N')
    responsavel_id = models.IntegerField(null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'leads'
        ordering = ['-data_cadastro']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['responsavel_id']),
        ]

    def __str__(self):
        return self.nome


class Oportunidades(models.Model):
    STATUS_CHOICES = [
        ('A', 'Aberta'),
        ('G', 'Ganha'),
        ('P', 'Perdida'),
    ]

    titulo = models.CharField(max_length=150)
    lead = models.ForeignKey('Leads', on_delete=models.PROTECT, null=True, blank=True)
    cliente = models.ForeignKey('Clientes', on_delete=models.PROTECT, null=True, blank=True)
    etapa = models.ForeignKey('EtapasFunil', on_delete=models.PROTECT, null=True, blank=True)
    valor_estimado = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    probabilidade = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')
    origem = models.CharField(max_length=50, null=True, blank=True)
    responsavel_id = models.IntegerField(null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    data_fechamento = models.DateTimeField(null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'oportunidades'
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['responsavel_id']),
        ]

    def __str__(self):
        return self.titulo


class AtividadesCRM(models.Model):
    oportunidade = models.ForeignKey('Oportunidades', on_delete=models.CASCADE, related_name='atividades')
    tipo = models.CharField(max_length=50)
    data_agendada = models.DateTimeField(null=True, blank=True)
    concluida = models.BooleanField(default=False)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    usuario_id = models.IntegerField(null=True, blank=True)
    descricao = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'atividades_crm'
        ordering = ['-data_agendada']
        indexes = [
            models.Index(fields=['concluida']),
            models.Index(fields=['usuario_id']),
        ]

    def __str__(self):
        return f"{self.tipo} - {self.oportunidade_id}"


class PropostasVenda(models.Model):
    STATUS_CHOICES = [
        ('R', 'Rascunho'),
        ('E', 'Enviada'),
        ('A', 'Aceita'),
        ('N', 'Negada'),
    ]

    oportunidade = models.ForeignKey('Oportunidades', on_delete=models.PROTECT, related_name='propostas')
    numero = models.CharField(max_length=30, db_index=True)
    data_emissao = models.DateTimeField(null=True, blank=True)
    validade = models.DateField(null=True, blank=True)
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='R')
    observacoes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'propostas_venda'
        ordering = ['-data_emissao']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['numero']),
        ]

    def __str__(self):
        return f"Proposta {self.numero}"


class ItensPropostaVenda(models.Model):
    proposta = models.ForeignKey('PropostasVenda', on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey('Produtos', on_delete=models.PROTECT)
    quantidade = models.DecimalField(max_digits=15, decimal_places=4, default=Decimal('0.0000'))
    valor_unitario = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    desconto = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        db_table = 'itens_proposta_venda'
        indexes = [
            models.Index(fields=['produto']),
        ]

    def __str__(self):
        return f"Item Proposta {self.proposta_id}"

class ContagensInventario(models.Model):
    inventario_id = models.ForeignKey('Inventarios', on_delete=models.PROTECT, null=True, blank=True)
    produto_id = models.ForeignKey('Produtos', on_delete=models.PROTECT, null=True, blank=True)
    lote_id = models.ForeignKey('Lotes', on_delete=models.PROTECT, null=True, blank=True)
    quantidade_sistema = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    quantidade_contagem = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    divergencia = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    usuario_contagem_id = models.IntegerField(null=True, blank=True)
    data_contagem = models.DateTimeField(null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'contagens_inventario'

    def __str__(self):
        return f"Contagem {self.id}"

from django.db import models
from decimal import Decimal

class ContasPagar(models.Model):
    STATUS_CHOICES = [
        ('A', 'Aberto'),
        ('P', 'Pago'),
        ('C', 'Cancelado'),
    ]

    data = models.DateTimeField(
        verbose_name='Data de Emissão',
        null=True,
        blank=True
    )
    valor = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor Original',
        default=Decimal('0.00')
    )
    fornecedor = models.ForeignKey(
        'Fornecedores',
        on_delete=models.PROTECT,
        related_name='contas_pagar',
        verbose_name='Fornecedor',
        null=True,
        blank=True
    )
    vencimento = models.DateTimeField(
        verbose_name='Data de Vencimento',
        null=True,
        blank=True
    )
    valor_total_pago = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor Total Pago',
        default=Decimal('0.00')
    )
    historico = models.TextField(
        verbose_name='Histórico',
        null=True,
        blank=True
    )
    forma_pagamento = models.CharField(
        max_length=50,
        verbose_name='Forma de Pagamento',
        null=True,
        blank=True
    )
    condicoes = models.CharField(
        max_length=100,
        verbose_name='Condições de Pagamento',
        null=True,
        blank=True
    )
    confirmacao = models.CharField(
        max_length=50,
        verbose_name='Confirmação',
        null=True,
        blank=True
    )
    juros = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Juros',
        default=Decimal('0.00')
    )
    tarifas = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Tarifas',
        default=Decimal('0.00')
    )
    numero_duplicata = models.CharField(
        max_length=50,
        verbose_name='Número da Duplicata',
        null=True,
        blank=True
    )
    data_pagamento = models.DateTimeField(
        verbose_name='Data de Pagamento',
        null=True,
        blank=True
    )
    valor_pago = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor Pago',
        default=Decimal('0.00')
    )
    local = models.CharField(
        max_length=100,
        verbose_name='Local de Pagamento',
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='A',
        verbose_name='Status'
    )
    conta = models.ForeignKey(
        'ContasBancarias',
        on_delete=models.PROTECT,
        related_name='contas_pagar',
        verbose_name='Conta Bancária',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'contas_pagar'
        verbose_name = 'Conta a Pagar'
        verbose_name_plural = 'Contas a Pagar'
        ordering = ['-data', '-vencimento']
        indexes = [
            models.Index(fields=['data']),
            models.Index(fields=['vencimento']),
            models.Index(fields=['fornecedor']),
            models.Index(fields=['status']),
            models.Index(fields=['data_pagamento']),
        ]

    def __str__(self):
        return f"CP {self.id} - {self.fornecedor} - {self.valor}"

    def clean(self):
        # Atualiza o valor total pago
        self.valor_total_pago = (
            (self.valor_pago or Decimal('0.00')) +
            (self.juros or Decimal('0.00')) +
            (self.tarifas or Decimal('0.00'))
        )
        
        # Atualiza o status se tiver pagamento
        if self.data_pagamento and self.valor_pago:
            if self.valor_pago >= self.valor:
                self.status = 'P'
            
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def dias_atraso(self):
        """Calcula os dias de atraso do pagamento"""
        if not self.vencimento:
            return 0
        if self.status == 'P':
            data_ref = self.data_pagamento
        else:
            data_ref = datetime.now()
        
        if data_ref and data_ref > self.vencimento:
            return (data_ref - self.vencimento).days
        return 0

    @property
    def saldo(self):
        """Retorna o saldo a pagar"""
        return self.valor - (self.valor_pago or Decimal('0.00'))


class ContasReceber(models.Model):
    STATUS_CHOICES = [
        ('A', 'Aberto'),
        ('P', 'Pago'),
        ('C', 'Cancelado'),
    ]

    documento = models.CharField(
        max_length=50,
        verbose_name='Documento',
        null=True,
        blank=True
    )
    data = models.DateTimeField(
        verbose_name='Data de Emissão',
        null=True,
        blank=True
    )
    valor = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor Original',
        default=Decimal('0.00')
    )
    cliente = models.ForeignKey(
        'Clientes',
        on_delete=models.PROTECT,
        related_name='contas_receber',
        verbose_name='Cliente',
        null=True,
        blank=True
    )
    vencimento = models.DateTimeField(
        verbose_name='Data de Vencimento',
        null=True,
        blank=True
    )
    valor_total_pago = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor Total Pago',
        default=Decimal('0.00')
    )
    historico = models.TextField(
        verbose_name='Histórico',
        null=True,
        blank=True
    )
    forma_pagamento = models.CharField(
        max_length=50,
        verbose_name='Forma de Pagamento',
        null=True,
        blank=True
    )
    condicoes = models.CharField(
        max_length=100,
        verbose_name='Condições de Pagamento',
        null=True,
        blank=True
    )
    confirmacao = models.CharField(
        max_length=50,
        verbose_name='Confirmação',
        null=True,
        blank=True
    )
    juros = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Juros',
        default=Decimal('0.00')
    )
    tarifas = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Tarifas',
        default=Decimal('0.00')
    )
    nosso_numero = models.CharField(
        max_length=50,
        verbose_name='Nosso Número',
        null=True,
        blank=True
    )
    recebido = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor Recebido',
        default=Decimal('0.00')
    )
    data_pagamento = models.DateTimeField(
        verbose_name='Data de Pagamento',
        null=True,
        blank=True
    )
    local = models.CharField(
        max_length=100,
        verbose_name='Local de Pagamento',
        null=True,
        blank=True
    )
    conta = models.ForeignKey(
        'ContasBancarias',
        on_delete=models.PROTECT,
        related_name='contas_receber',
        verbose_name='Conta Bancária',
        null=True,
        blank=True
    )
    impresso = models.BooleanField(
        verbose_name='Impresso',
        default=False
    )
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='A',
        verbose_name='Status'
    )
    comanda = models.CharField(
        max_length=50,
        verbose_name='Comanda',
        null=True,
        blank=True
    )
    repassado_factory = models.BooleanField(
        verbose_name='Repassado para Factory',
        default=False
    )
    factory = models.CharField(
        max_length=100,
        verbose_name='Factory',
        null=True,
        blank=True
    )
    valor_factory = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor Factory',
        default=Decimal('0.00')
    )
    status_factory = models.CharField(
        max_length=50,
        verbose_name='Status Factory',
        null=True,
        blank=True
    )
    valor_pago_factory = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor Pago Factory',
        default=Decimal('0.00')
    )
    cartorio = models.BooleanField(
        verbose_name='Em Cartório',
        default=False
    )
    protesto = models.BooleanField(
        verbose_name='Protestado',
        default=False
    )
    desconto = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Desconto',
        default=Decimal('0.00')
    )
    data_pagto_factory = models.DateTimeField(
        verbose_name='Data Pagamento Factory',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'contas_receber'
        verbose_name = 'Conta a Receber'
        verbose_name_plural = 'Contas a Receber'
        ordering = ['-data', '-vencimento']
        indexes = [
            models.Index(fields=['data']),
            models.Index(fields=['vencimento']),
            models.Index(fields=['cliente']),
            models.Index(fields=['status']),
            models.Index(fields=['data_pagamento']),
            models.Index(fields=['nosso_numero']),
            models.Index(fields=['documento']),
        ]

    def __str__(self):
        return f"CR {self.id} - {self.cliente} - {self.valor}"

    def clean(self):
        # Calcula o valor total pago
        self.valor_total_pago = (
            (self.recebido or Decimal('0.00')) +
            (self.juros or Decimal('0.00')) +
            (self.tarifas or Decimal('0.00')) -
            (self.desconto or Decimal('0.00'))
        )
        
        # Atualiza o status se tiver pagamento
        if self.data_pagamento and self.recebido:
            if self.recebido >= self.valor:
                self.status = 'P'
            
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def dias_atraso(self):
        """Calcula os dias de atraso do recebimento"""
        if not self.vencimento:
            return 0
        if self.status == 'P':
            data_ref = self.data_pagamento
        else:
            data_ref = datetime.now()
        
        if data_ref and data_ref > self.vencimento:
            return (data_ref - self.vencimento).days
        return 0

    @property
    def saldo(self):
        """Retorna o saldo a receber"""
        return self.valor - (self.recebido or Decimal('0.00'))

    @property
    def valor_final(self):
        """Retorna o valor com juros e descontos"""
        return (
            self.valor +
            (self.juros or Decimal('0.00')) -
            (self.desconto or Decimal('0.00'))
        )

class ContratosLocacao(models.Model):
    cliente = models.ForeignKey('Clientes', on_delete=models.PROTECT, null=True, blank=True)
    contrato = models.CharField(max_length=100, null=True, blank=True)
    #cliente = models.CharField(max_length=100, null=True, blank=True)
    tipocontrato = models.CharField(max_length=20, null=True, blank=True)
    renovado = models.CharField(max_length=100, null=True, blank=True)
    totalmaquinas = models.CharField(max_length=100, null=True, blank=True)
    valorcontrato = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    numeroparcelas = models.CharField(max_length=100, null=True, blank=True)
    valorpacela = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Aqui está o campo
    referencia = models.CharField(max_length=100, null=True, blank=True)
    data = models.DateField(null=True, blank=True)
    inicio = models.DateField(null=True, blank=True)
    fim = models.DateField(null=True, blank=True)
    ultimoatendimento = models.DateField(null=True, blank=True)
    nmaquinas = models.CharField(max_length=100, null=True, blank=True)
    clientereal = models.CharField(max_length=100, null=True, blank=True)
    tipocontratoreal = models.CharField(max_length=100, null=True, blank=True)
    obs = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'contratos_locacao'

    def __str__(self):
        return f"Contrato {self.contrato} - {self.cliente}"

class ItensContratoLocacao(models.Model):
    contrato = models.ForeignKey('ContratosLocacao', on_delete=models.PROTECT, null=True, blank=True)
    numeroserie = models.CharField(max_length=30, null=True, blank=True)
    modelo = models.CharField(max_length=50, null=True, blank=True)
    categoria = models.ForeignKey('CategoriasProdutos', on_delete=models.PROTECT, null=True, blank=True)
    inicio = models.DateField(null=True, blank=True)
    fim = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'itens_contrato_locacao'

    def __str__(self):
        return f"Item {self.produto_id} - Contrato {self.contrato_id}"

class CustosAdicionaisFrete(models.Model):
    frete = models.ForeignKey('Fretes', on_delete=models.PROTECT, null=True, blank=True)
    tipo_custo = models.CharField(max_length=50)
    descricao = models.TextField(null=True, blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'custos_adicionais_frete'

    def __str__(self):
        return f"{self.tipo_custo} - {self.valor}"

class Despesas(models.Model):
    codigo = models.IntegerField()
    descricao = models.CharField(max_length=50)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    ativo = models.BooleanField(null=True, blank=True, default=True)

    class Meta:
        db_table = 'despesas'

    def __str__(self):
        return self.descricao

class Empresas(models.Model):
    razao_social = models.CharField(max_length=100)
    nome_fantasia = models.CharField(max_length=100, null=True, blank=True)
    cnpj = models.CharField(max_length=14)
    ie = models.CharField(max_length=20, null=True, blank=True)
    endereco = models.CharField(max_length=100, null=True, blank=True)
    numero = models.CharField(max_length=10, null=True, blank=True)
    complemento = models.CharField(max_length=50, null=True, blank=True)
    bairro = models.CharField(max_length=50, null=True, blank=True)
    cidade = models.CharField(max_length=50, null=True, blank=True)
    estado = models.CharField(max_length=2, null=True, blank=True)
    cep = models.CharField(max_length=8, null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    ativo = models.BooleanField(null=True, blank=True, default=True)

    class Meta:
        db_table = 'empresas'

    def __str__(self):
        return self.razao_social

class MovimentacoesEstoque(models.Model):
    data_movimentacao = models.DateTimeField()
    tipo_movimentacao = models.ForeignKey('TiposMovimentacaoEstoque', on_delete=models.PROTECT, null=True, blank=True)
    produto = models.ForeignKey('Produtos', on_delete=models.PROTECT, null=True, blank=True)
    lote_id = models.ForeignKey('Lotes', on_delete=models.PROTECT, null=True, blank=True)
    local_origem_id = models.ForeignKey('LocaisEstoque', on_delete=models.PROTECT, null=True, blank=True, related_name='movimentacoes_origem')
    local_destino_id = models.ForeignKey('LocaisEstoque', on_delete=models.PROTECT, null=True, blank=True, related_name='movimentacoes_destino')
    quantidade = models.DecimalField(max_digits=10, decimal_places=3)
    custo_unitario = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    nota_fiscal_entrada = models.ForeignKey('NotasFiscaisEntrada', on_delete=models.PROTECT, null=True, blank=True)
    nota_fiscal_saida = models.ForeignKey('NotasFiscaisSaida', on_delete=models.PROTECT, null=True, blank=True)
    usuario_id = models.IntegerField(null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)
    documento_referencia = models.CharField(max_length=50, null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'movimentacoes_estoque'

    def __str__(self):
        return f"Movimentação {self.id}"


class OcorrenciasFrete(models.Model):
    frete = models.ForeignKey('Fretes', on_delete=models.PROTECT, null=True, blank=True)
    data_ocorrencia = models.DateTimeField()
    tipo_ocorrencia = models.CharField(max_length=50)
    descricao = models.TextField(null=True, blank=True)
    local_ocorrencia = models.CharField(max_length=100, null=True, blank=True)
    responsavel = models.CharField(max_length=100, null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'ocorrencias_frete'

    def __str__(self):
        return f"{self.tipo_ocorrencia} - {self.data_ocorrencia}"

class PagamentosFuncionarios(models.Model):
    funcionario_id = models.ForeignKey('Funcionarios', on_delete=models.PROTECT, null=True, blank=True)
    tipo_pagamento = models.CharField(max_length=50)
    competencia = models.DateField()
    salario_base = models.DecimalField(max_digits=10, decimal_places=2)
    horas_extras = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_horas_extras = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    comissoes = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    descontos = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    inss = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    irrf = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fgts = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_liquido = models.DecimalField(max_digits=10, decimal_places=2)
    data_pagamento = models.DateField(null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'pagamentos_funcionarios'

    def __str__(self):
        return f"Pagamento {self.funcionario_id} - {self.competencia}"

class PosicoesEstoque(models.Model):
    local_id = models.ForeignKey('LocaisEstoque', on_delete=models.PROTECT, null=True, blank=True)
    codigo = models.CharField(max_length=20)
    descricao = models.CharField(max_length=100, null=True, blank=True)
    ativo = models.BooleanField(null=True, blank=True, default=True)

    class Meta:
        db_table = 'posicoes_estoque'

    def __str__(self):
        return f"{self.codigo} - {self.descricao}"

class Produtos(models.Model):
    codigo = models.CharField(max_length=20)
    nome = models.CharField(max_length=100)
    descricao = models.TextField(null=True, blank=True)
    referencia = models.CharField(max_length=100, null=True, blank=True)
    grupo_id = models.IntegerField(null=True, blank=True)
    unidade_medida = models.CharField(max_length=10, null=True, blank=True)
    sku = models.CharField(max_length=60, null=True, blank=True)
    ean = models.CharField(max_length=14, null=True, blank=True)
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    margem_lucro = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    estoque_minimo = models.IntegerField(null=True, blank=True)
    ponto_reposicao = models.IntegerField(null=True, blank=True)
    lead_time_dias = models.IntegerField(null=True, blank=True)
    estoque_atual = models.IntegerField(null=True, blank=True, default=0)
    disponivel_locacao = models.BooleanField(null=True, blank=True, default=False)
    valor_locacao_diaria = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    ativo = models.BooleanField(null=True, blank=True, default=True)
    controla_lote = models.BooleanField(null=True, blank=True, default=False)
    controla_validade = models.BooleanField(null=True, blank=True, default=False)

    class Meta:
        db_table = 'produtos'

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

class ProdutoFiscal(models.Model):
    produto_id = models.ForeignKey('Produtos', on_delete=models.PROTECT)
    ncm = models.CharField(max_length=20, null=True, blank=True)
    cst = models.CharField(max_length=10, null=True, blank=True)
    cfop = models.CharField(max_length=10, null=True, blank=True)
    origem = models.CharField(max_length=20, null=True, blank=True)
    unidade_tributavel = models.CharField(max_length=10, null=True, blank=True)
    aliquota_icms = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    aliquota_ipi = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    aliquota_pis = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    aliquota_cofins = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)
    ativo = models.BooleanField(null=True, blank=True, default=True)

    class Meta:
        db_table = 'produtos_fiscal'

    def __str__(self):
        return f"Fiscal {self.produto_id}"

class ProdutoVariacao(models.Model):
    produto_id = models.ForeignKey('Produtos', on_delete=models.PROTECT, related_name='variacoes')
    codigo = models.CharField(max_length=50)
    descricao = models.CharField(max_length=120, null=True, blank=True)
    atributos = models.JSONField(null=True, blank=True)
    ativo = models.BooleanField(null=True, blank=True, default=True)

    class Meta:
        db_table = 'produtos_variacoes'

    def __str__(self):
        return f"{self.produto_id} - {self.codigo}"

class ProdutoComposicao(models.Model):
    produto_pai_id = models.ForeignKey('Produtos', on_delete=models.PROTECT, related_name='componentes')
    produto_componente_id = models.ForeignKey('Produtos', on_delete=models.PROTECT, related_name='utilizado_em')
    quantidade = models.DecimalField(max_digits=10, decimal_places=3)
    unidade_medida = models.CharField(max_length=10, null=True, blank=True)
    custo_proporcional = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ativo = models.BooleanField(null=True, blank=True, default=True)

    class Meta:
        db_table = 'produtos_composicao'

    def __str__(self):
        return f"{self.produto_pai_id} -> {self.produto_componente_id}"

class ProdutoConversaoUnidade(models.Model):
    produto_id = models.ForeignKey('Produtos', on_delete=models.PROTECT)
    unidade_origem = models.CharField(max_length=10)
    unidade_destino = models.CharField(max_length=10)
    fator_conversao = models.DecimalField(max_digits=12, decimal_places=6)
    arredondamento = models.CharField(max_length=10, null=True, blank=True)
    ativo = models.BooleanField(null=True, blank=True, default=True)

    class Meta:
        db_table = 'produtos_conversao_unidade'

    def __str__(self):
        return f"{self.produto_id} {self.unidade_origem}->{self.unidade_destino}"

class ProdutoHistoricoPreco(models.Model):
    produto_id = models.ForeignKey('Produtos', on_delete=models.PROTECT)
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    origem = models.CharField(max_length=40, null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'produtos_historico_precos'

    def __str__(self):
        return f"Histórico {self.produto_id} ({self.data_inicio})"

class TabelaPreco(models.Model):
    descricao = models.CharField(max_length=100)
    data_inicio = models.DateField(null=True, blank=True)
    data_fim = models.DateField(null=True, blank=True)
    moeda = models.CharField(max_length=10, null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)
    ativo = models.BooleanField(null=True, blank=True, default=True)

    class Meta:
        db_table = 'tabelas_precos'

    def __str__(self):
        return self.descricao

class TabelaPrecoItem(models.Model):
    tabela_id = models.ForeignKey('TabelaPreco', on_delete=models.PROTECT)
    produto_id = models.ForeignKey('Produtos', on_delete=models.PROTECT)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    preco_minimo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    desconto_maximo = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    quantidade_minima = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    ativo = models.BooleanField(null=True, blank=True, default=True)

    class Meta:
        db_table = 'tabelas_precos_itens'

    def __str__(self):
        return f"{self.tabela_id} - {self.produto_id}"

class PoliticaDesconto(models.Model):
    produto_id = models.ForeignKey('Produtos', on_delete=models.PROTECT, null=True, blank=True)
    tabela_id = models.ForeignKey('TabelaPreco', on_delete=models.PROTECT, null=True, blank=True)
    cliente_id = models.ForeignKey('Clientes', on_delete=models.PROTECT, null=True, blank=True)
    percentual = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantidade_minima = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    data_inicio = models.DateField(null=True, blank=True)
    data_fim = models.DateField(null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)
    ativo = models.BooleanField(null=True, blank=True, default=True)

    class Meta:
        db_table = 'politicas_desconto'

    def __str__(self):
        return f"Desconto {self.produto_id or self.tabela_id}"

class ProdutoSubstituto(models.Model):
    produto_id = models.ForeignKey('Produtos', on_delete=models.PROTECT, related_name='substitutos')
    produto_substituto_id = models.ForeignKey('Produtos', on_delete=models.PROTECT, related_name='substitui')
    motivo = models.CharField(max_length=120, null=True, blank=True)
    ativo = models.BooleanField(null=True, blank=True, default=True)

    class Meta:
        db_table = 'produtos_substitutos'

    def __str__(self):
        return f"{self.produto_id} -> {self.produto_substituto_id}"

class ProdutoCustoLocal(models.Model):
    produto_id = models.ForeignKey('Produtos', on_delete=models.PROTECT)
    local_id = models.ForeignKey('LocaisEstoque', on_delete=models.PROTECT, null=True, blank=True)
    custo_medio = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    ultima_atualizacao = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'produtos_custo_local'

    def __str__(self):
        return f"{self.produto_id} - {self.local_id}"

class RegioesEntrega(models.Model):
    transportadora_id = models.ForeignKey('Transportadoras', on_delete=models.PROTECT, null=True, blank=True)
    descricao = models.CharField(max_length=100)
    cep_inicial = models.CharField(max_length=8, null=True, blank=True)
    cep_final = models.CharField(max_length=8, null=True, blank=True)
    prazo_entrega = models.IntegerField(null=True, blank=True)
    valor_base = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_kg_adicional = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_seguro_percentual = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)
    ativo = models.BooleanField(null=True, blank=True, default=True)

    class Meta:
        db_table = 'regioes_entrega'

    def __str__(self):
        return self.descricao

class SaldosEstoque(models.Model):
    produto_id = models.ForeignKey('Produtos', on_delete=models.PROTECT, null=True, blank=True)
    local_id = models.ForeignKey('LocaisEstoque', on_delete=models.PROTECT, null=True, blank=True)
    lote_id = models.ForeignKey('Lotes', on_delete=models.PROTECT, null=True, blank=True)
    quantidade = models.DecimalField(max_digits=10, decimal_places=3, default=0.0)
    quantidade_reservada = models.DecimalField(max_digits=10, decimal_places=3, default=0.0)
    custo_medio = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    ultima_movimentacao = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'saldos_estoque'

    def __str__(self):
        return f"Saldo {self.produto_id} - {self.local_id}"

class TabelasFrete(models.Model):
    transportadora_id = models.ForeignKey('Transportadoras', on_delete=models.PROTECT, null=True, blank=True)
    descricao = models.CharField(max_length=100)
    data_inicio_vigencia = models.DateField()
    data_fim_vigencia = models.DateField(null=True, blank=True)
    percentual_desconto = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)
    ativo = models.BooleanField(null=True, blank=True, default=True)

    class Meta:
        db_table = 'tabelas_frete'

    def __str__(self):
        return self.descricao

class TiposMovimentacaoEstoque(models.Model):
    codigo = models.CharField(max_length=10)
    descricao = models.CharField(max_length=50)
    tipo = models.CharField(max_length=1)
    movimenta_custo = models.BooleanField(null=True, blank=True, default=True)
    ativo = models.BooleanField(null=True, blank=True, default=True)

    class Meta:
        db_table = 'tipos_movimentacao_estoque'

    def __str__(self):
        return f"{self.codigo} - {self.descricao}"

class Transportadoras(models.Model):
    razao_social = models.CharField(max_length=100)
    nome = models.CharField(max_length=100, null=True, blank=True)
    cnpj = models.CharField(max_length=20, null=True, blank=True)
    ie = models.CharField(max_length=20, null=True, blank=True)
    endereco = models.CharField(max_length=100, null=True, blank=True)
    numero = models.CharField(max_length=10, null=True, blank=True)
    complemento = models.CharField(max_length=50, null=True, blank=True)
    bairro = models.CharField(max_length=50, null=True, blank=True)
    cidade = models.CharField(max_length=50, null=True, blank=True)
    estado = models.CharField(max_length=2, null=True, blank=True)
    cep = models.CharField(max_length=15, null=True, blank=True)
    fone = models.CharField(max_length=20, null=True, blank=True)
    celular = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    contato_principal = models.CharField(max_length=100, null=True, blank=True)
    site_rastreamento = models.CharField(max_length=200, null=True, blank=True)
    formato_codigo_rastreio = models.CharField(max_length=50, null=True, blank=True)
    prazo_medio_entrega = models.IntegerField(null=True, blank=True)
    valor_minimo_frete = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    percentual_seguro = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    ativo = models.BooleanField(null=True, blank=True, default=True)
    contato = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'transportadoras'

    def __str__(self):
        return self.razao_social
    
class Fornecedores(models.Model):
    tipo_pessoa = models.CharField(max_length=1, null=True, blank=True, default='F')  # F para Física ou J para Jurídica
    nome = models.CharField(max_length=100)
    cpf_cnpj = models.CharField(max_length=14, null=True, blank=True)
    rg_ie = models.CharField(max_length=20, null=True, blank=True)
    endereco = models.CharField(max_length=100, null=True, blank=True)
    numero = models.CharField(max_length=10, null=True, blank=True)
    complemento = models.CharField(max_length=50, null=True, blank=True)
    bairro = models.CharField(max_length=50, null=True, blank=True)
    cidade = models.CharField(max_length=50, null=True, blank=True)
    estado = models.CharField(max_length=2, null=True, blank=True)  # Corrigido para 2 caracteres
    cep = models.CharField(max_length=11, null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    contato_nome = models.CharField(max_length=100, null=True, blank=True)
    contato_telefone = models.CharField(max_length=20, null=True, blank=True)
    tipo = models.CharField(max_length=50, null=True, blank=True)  # Novo campo tipo
    especificacao = models.TextField(null=True, blank=True)  # Campo especificacao do Access
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True)  # Removido default CURRENT_TIMESTAMP
    ativo = models.BooleanField(null=True, blank=True, default=True)

    class Meta:
        db_table = 'fornecedores'

    def __str__(self):
        return self.nome
    
class Funcionarios(models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=11,null=True, blank=True)
    rg = models.CharField(max_length=20, null=True, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    data_admissao = models.DateField(null=True, blank=True)
    data_demissao = models.DateField(null=True, blank=True)
    cargo = models.CharField(max_length=50, null=True, blank=True)
    salario_base = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    endereco = models.CharField(max_length=100, null=True, blank=True)
    numero = models.CharField(max_length=10, null=True, blank=True)
    complemento = models.CharField(max_length=50, null=True, blank=True)
    bairro = models.CharField(max_length=50, null=True, blank=True)
    cidade = models.CharField(max_length=50, null=True, blank=True)
    estado = models.CharField(max_length=2, null=True, blank=True)
    cep = models.CharField(max_length=8, null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    banco = models.CharField(max_length=50, null=True, blank=True)
    agencia = models.CharField(max_length=10, null=True, blank=True)
    conta = models.CharField(max_length=20, null=True, blank=True)
    pix = models.CharField(max_length=100, null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    ativo = models.BooleanField(null=True, blank=True, default=True)

    class Meta:
        db_table = 'funcionarios'

    def __str__(self):
        return self.nome

class Grupos(models.Model):
    nome = models.CharField(max_length=50)

    class Meta:
        db_table = 'grupos'

    def __str__(self):
        return self.nome

class HistoricoRastreamento(models.Model):
    frete_id = models.ForeignKey('Fretes', on_delete=models.PROTECT, null=True, blank=True)
    data_evento = models.DateTimeField()
    status = models.CharField(max_length=50)
    localizacao = models.CharField(max_length=100, null=True, blank=True)
    descricao = models.TextField(null=True, blank=True)
    data_consulta = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'historico_rastreamento'

    def __str__(self):
        return f"{self.status} - {self.data_evento}"

class Inventarios(models.Model):
    codigo = models.CharField(max_length=20)
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True)
    tipo = models.CharField(max_length=20, null=True, blank=True)
    local_id = models.ForeignKey('LocaisEstoque', on_delete=models.PROTECT, null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)
    usuario_abertura_id = models.IntegerField(null=True, blank=True)
    usuario_fechamento_id = models.IntegerField(null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'inventarios'

    def __str__(self):
        return f"{self.codigo} - {self.status}"

from django.db import models
from decimal import Decimal

class NotasFiscaisEntrada(models.Model):
    # Campos chave e relacionamentos
    id = models.AutoField(primary_key=True)  # Alterado para AutoField
    numero_nota = models.CharField(max_length=20, db_index=True)  # Removido unique=True
    serie_nota = models.CharField(max_length=5, null=True, blank=True)
    fornecedor = models.ForeignKey(
        'Fornecedores',
        on_delete=models.PROTECT,
        related_name='notas_fiscais_entrada',
        null=True, blank=True
    )
    Produto = models.ForeignKey(
        'Produtos',
        on_delete=models.PROTECT,
        related_name='notas_fiscais_entrada',
        null=True, blank=True
    )
    frete = models.ForeignKey(
        'Fretes',
        on_delete=models.PROTECT,
        related_name='notas_fiscais_entrada',
        null=True, blank=True
    )

    tipo_frete = models.CharField(max_length=10, null=True, blank=True)

    # Datas
    data_emissao = models.DateTimeField(null=True, blank=True)
    data_entrada = models.DateTimeField(null=True, blank=True)

    # Valores
    valor_produtos = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    base_calculo_icms = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    valor_icms = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    valor_ipi = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    valor_icms_st = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    base_calculo_st = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    valor_desconto = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    valor_frete = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    outras_despesas = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    outros_encargos = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    valor_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )

    # Informações fiscais
    chave_nfe = models.CharField(max_length=44, null=True, blank=True, db_index=True)
    protocolo = models.CharField(max_length=20, null=True, blank=True)
    natureza_operacao = models.CharField(max_length=100, null=True, blank=True)
    cfop = models.CharField(max_length=5, null=True, blank=True)

    # Informações comerciais
    forma_pagamento = models.CharField(max_length=50, null=True, blank=True)
    condicoes_pagamento = models.CharField(max_length=100, null=True, blank=True)
    parcelas = models.CharField(max_length=100, null=True, blank=True)
    operacao = models.CharField(max_length=50, null=True, blank=True)

    # Informações adicionais
    comprador = models.CharField(max_length=100, null=True, blank=True)
    operador = models.CharField(max_length=100, null=True, blank=True)
    observacao = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'notas_fiscais_entrada'
        verbose_name = 'Nota Fiscal de entrada'
        verbose_name_plural = 'Notas Fiscais de entrada'
        ordering = ['-data_emissao']
        indexes = [
            models.Index(fields=['data_emissao']),
            models.Index(fields=['data_entrada']),
            models.Index(fields=['fornecedor', 'numero_nota']),
            models.Index(fields=['id']),  # Adicionado índice explícito no id
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['fornecedor', 'numero_nota', 'serie_nota'],
                name='unique_nota_fiscal_fornecedor'
            )
        ]

    def __str__(self):
        return f"NF {self.numero_nota} - {self.fornecedor}"

    def clean(self):
        self.valor_total = (
            self.valor_produtos
            + self.valor_frete
            + self.valor_ipi
            + self.valor_icms_st
            + self.outras_despesas
            + self.outros_encargos
            - self.valor_desconto
        )
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class ItensNfEntrada(models.Model):
    id = models.AutoField(primary_key=True)  # Alterado para AutoField
    nota_fiscal = models.ForeignKey(
        NotasFiscaisEntrada,  # Alterado para referência direta
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='Nota Fiscal',
        db_column='nota_fiscal_id'  # Adicionado db_column explícito
    )
    data = models.DateTimeField(verbose_name='Data', null=True, blank=True)
    produto = models.ForeignKey(
        'Produtos',
        on_delete=models.PROTECT,
        verbose_name='Produto',
        related_name='itens_nf_entrada'
    )
    quantidade = models.DecimalField(
        max_digits=15, 
        decimal_places=4, 
        verbose_name='Quantidade',
        null=True,
        blank=True,
        default=Decimal('0.0000')
    )
    valor_unitario = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name='Valor Unitário',
        null=True,
        blank=True,
        default=Decimal('0.00')
    )
    valor_total = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name='Valor Total',
        null=True,
        blank=True,
        default=Decimal('0.00')
    )
    percentual_ipi = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name='Percentual IPI', 
        default=Decimal('0.00'),
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=50, 
        verbose_name='Status',
        null=True,
        blank=True
    )
    aliquota = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name='Alíquota', 
        default=Decimal('0.00'),
        null=True,
        blank=True
    )
    desconto = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name='Desconto', 
        default=Decimal('0.00'),
        null=True,
        blank=True
    )
    cfop = models.CharField(
        max_length=5, 
        verbose_name='CFOP',
        null=True,
        blank=True
    )
    base_substituicao = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name='Base de Cálculo Substituição',
        default=Decimal('0.00'),
        null=True,
        blank=True
    )
    icms_substituicao = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name='ICMS Substituição',
        default=Decimal('0.00'),
        null=True,
        blank=True
    )
    outras_despesas = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name='Outras Despesas',
        default=Decimal('0.00'),
        null=True,
        blank=True
    )
    frete = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name='Frete', 
        default=Decimal('0.00'),
        null=True,
        blank=True
    )
    aliquota_substituicao = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name='Alíquota Substituição',
        default=Decimal('0.00'),
        null=True,
        blank=True
    )
    ncm = models.CharField(
        max_length=10, 
        verbose_name='NCM',
        null=True,
        blank=True
    )
    controle = models.CharField(
        max_length=50, 
        verbose_name='Controle',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'itens_nf_entrada'
        verbose_name = 'Item da NFE'
        verbose_name_plural = 'Itens da NFE'
        ordering = ['nota_fiscal', 'id']
        indexes = [
            models.Index(fields=['nota_fiscal']),
            models.Index(fields=['produto']),
            models.Index(fields=['data']),
        ]

    def __str__(self):
        return f"Item {self.id} - NF {self.nota_fiscal}"

    def clean(self):
        if self.quantidade is not None and self.valor_unitario is not None:
            total = self.quantidade * self.valor_unitario
            if self.desconto:
                total -= self.desconto
            self.valor_total = total
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class RequisicoesCompra(models.Model):
    STATUS_CHOICES = [
        ('R', 'Rascunho'),
        ('A', 'Aprovada'),
        ('C', 'Cotada'),
        ('X', 'Cancelada'),
    ]

    numero_requisicao = models.CharField(max_length=30, db_index=True)
    solicitante_id = models.IntegerField(null=True, blank=True)
    fornecedor_sugerido = models.ForeignKey(
        'Fornecedores',
        on_delete=models.PROTECT,
        related_name='requisicoes_compra',
        null=True,
        blank=True
    )
    data_solicitacao = models.DateTimeField(null=True, blank=True)
    data_aprovacao = models.DateTimeField(null=True, blank=True)
    prioridade = models.CharField(max_length=20, null=True, blank=True)
    valor_estimado = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='R')
    observacoes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'requisicoes_compra'
        ordering = ['-data_solicitacao']
        indexes = [
            models.Index(fields=['numero_requisicao']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"REQ {self.numero_requisicao}"


class ItensRequisicaoCompra(models.Model):
    requisicao = models.ForeignKey(
        RequisicoesCompra,
        on_delete=models.CASCADE,
        related_name='itens'
    )
    produto = models.ForeignKey('Produtos', on_delete=models.PROTECT)
    quantidade = models.DecimalField(max_digits=15, decimal_places=4, default=Decimal('0.0000'))
    preco_estimado = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    observacoes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'itens_requisicao_compra'
        indexes = [
            models.Index(fields=['produto']),
        ]

    def __str__(self):
        return f"Item REQ {self.requisicao_id}"


class CotacoesCompra(models.Model):
    STATUS_CHOICES = [
        ('A', 'Aberta'),
        ('P', 'Aprovada'),
        ('X', 'Cancelada'),
    ]

    requisicao = models.ForeignKey(
        RequisicoesCompra,
        on_delete=models.PROTECT,
        related_name='cotacoes',
        null=True,
        blank=True
    )
    fornecedor = models.ForeignKey(
        'Fornecedores',
        on_delete=models.PROTECT,
        related_name='cotacoes_compra'
    )
    data_cotacao = models.DateTimeField(null=True, blank=True)
    validade = models.DateField(null=True, blank=True)
    condicoes_pagamento = models.CharField(max_length=100, null=True, blank=True)
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')
    observacoes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'cotacoes_compra'
        ordering = ['-data_cotacao']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['fornecedor']),
        ]

    def __str__(self):
        return f"COT {self.id} - {self.fornecedor}"


class ItensCotacaoCompra(models.Model):
    cotacao = models.ForeignKey(
        CotacoesCompra,
        on_delete=models.CASCADE,
        related_name='itens'
    )
    produto = models.ForeignKey('Produtos', on_delete=models.PROTECT)
    quantidade = models.DecimalField(max_digits=15, decimal_places=4, default=Decimal('0.0000'))
    valor_unitario = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    prazo_entrega_dias = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'itens_cotacao_compra'
        indexes = [
            models.Index(fields=['produto']),
        ]

    def __str__(self):
        return f"Item COT {self.cotacao_id}"


class PedidosCompra(models.Model):
    STATUS_CHOICES = [
        ('R', 'Rascunho'),
        ('A', 'Aprovado'),
        ('E', 'Enviado'),
        ('F', 'Recebido'),
        ('X', 'Cancelado'),
    ]

    numero_pedido = models.CharField(max_length=30, db_index=True)
    requisicao = models.ForeignKey(
        RequisicoesCompra,
        on_delete=models.PROTECT,
        related_name='pedidos',
        null=True,
        blank=True
    )
    cotacao = models.ForeignKey(
        CotacoesCompra,
        on_delete=models.PROTECT,
        related_name='pedidos',
        null=True,
        blank=True
    )
    fornecedor = models.ForeignKey(
        'Fornecedores',
        on_delete=models.PROTECT,
        related_name='pedidos_compra'
    )
    data_emissao = models.DateTimeField(null=True, blank=True)
    data_prevista = models.DateField(null=True, blank=True)
    data_aprovacao = models.DateTimeField(null=True, blank=True)
    condicoes_pagamento = models.CharField(max_length=100, null=True, blank=True)
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='R')
    observacoes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'pedidos_compra'
        ordering = ['-data_emissao']
        indexes = [
            models.Index(fields=['numero_pedido']),
            models.Index(fields=['status']),
            models.Index(fields=['fornecedor']),
        ]

    def __str__(self):
        return f"PC {self.numero_pedido}"


class ItensPedidoCompra(models.Model):
    pedido = models.ForeignKey(
        PedidosCompra,
        on_delete=models.CASCADE,
        related_name='itens'
    )
    produto = models.ForeignKey('Produtos', on_delete=models.PROTECT)
    quantidade = models.DecimalField(max_digits=15, decimal_places=4, default=Decimal('0.0000'))
    valor_unitario = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    desconto = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        db_table = 'itens_pedido_compra'
        indexes = [
            models.Index(fields=['produto']),
        ]

    def __str__(self):
        return f"Item PC {self.pedido_id}"


class Fretes(models.Model):
    transportadora = models.ForeignKey('Transportadoras', on_delete=models.PROTECT, null=True, blank=True)
    numero = models.CharField(max_length=20)
    tipo_fob_cif = models.CharField(max_length=20, null=True, blank=True)
    data_emissao = models.DateField(null=True, blank=True)
    data_entrada = models.DateField(null=True, blank=True)
    cfop = models.CharField(max_length=10, null=True, blank=True)
    valor_total = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    base_calculo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    aliquota = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    icms = models.DecimalField(max_digits=13, decimal_places=2, null=True, blank=True)
    ufcoleta = models.CharField(max_length=14, null=True, blank=True)
    municipiocoleta = models.CharField(max_length=50, null=True, blank=True)
    ibge = models.CharField(max_length=15, null=True, blank=True)
    tipo_cte = models.CharField(max_length=20, null=True, blank=True)
    chave = models.CharField(max_length=50, null=True, blank=True)
    fatura = models.CharField(max_length=50, null=True, blank=True)
    formulario = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'fretes'

    def __str__(self):
        return f"Frete {self.id} - {self.tipo_operacao}"


class ImpostosFiscais(models.Model):
    codigo = models.CharField(max_length=20, db_index=True)
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, null=True, blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        db_table = 'impostos_fiscais'
        ordering = ['nome']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['tipo']),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nome}"


class ApuracoesFiscais(models.Model):
    STATUS_CHOICES = [
        ('A', 'Aberta'),
        ('F', 'Fechada'),
    ]

    data_inicio = models.DateField()
    data_fim = models.DateField()
    data_apuracao = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')
    total_debitos = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_creditos = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    saldo = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    observacoes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'apuracoes_fiscais'
        ordering = ['-data_apuracao']
        indexes = [
            models.Index(fields=['data_inicio', 'data_fim']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Apuração {self.id} ({self.data_inicio} - {self.data_fim})"


class ItensApuracaoFiscal(models.Model):
    apuracao = models.ForeignKey(
        ApuracoesFiscais,
        on_delete=models.CASCADE,
        related_name='itens'
    )
    imposto = models.ForeignKey('ImpostosFiscais', on_delete=models.PROTECT)
    valor_debito = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    valor_credito = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    saldo = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        db_table = 'itens_apuracao_fiscal'
        indexes = [
            models.Index(fields=['imposto']),
        ]

    def __str__(self):
        return f"Item Apuração {self.apuracao_id} - {self.imposto}"


class OrdensProducao(models.Model):
    STATUS_CHOICES = [
        ('R', 'Rascunho'),
        ('A', 'Aprovada'),
        ('E', 'Em produção'),
        ('F', 'Finalizada'),
        ('X', 'Cancelada'),
    ]

    numero_ordem = models.CharField(max_length=30, db_index=True)
    produto_final = models.ForeignKey('Produtos', on_delete=models.PROTECT)
    local_id = models.ForeignKey('LocaisEstoque', on_delete=models.PROTECT, null=True, blank=True)
    quantidade_planejada = models.DecimalField(max_digits=15, decimal_places=4, default=Decimal('0.0000'))
    quantidade_produzida = models.DecimalField(max_digits=15, decimal_places=4, default=Decimal('0.0000'))
    data_inicio = models.DateTimeField(null=True, blank=True)
    data_fim = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='R')
    observacoes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'ordens_producao'
        ordering = ['-data_inicio']
        indexes = [
            models.Index(fields=['numero_ordem']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"OP {self.numero_ordem}"


class ItensOrdemProducao(models.Model):
    ordem = models.ForeignKey('OrdensProducao', on_delete=models.CASCADE, related_name='itens')
    produto_insumo = models.ForeignKey('Produtos', on_delete=models.PROTECT)
    quantidade = models.DecimalField(max_digits=15, decimal_places=4, default=Decimal('0.0000'))

    class Meta:
        db_table = 'itens_ordem_producao'
        indexes = [
            models.Index(fields=['produto_insumo']),
        ]

    def __str__(self):
        return f"Insumo {self.produto_insumo_id} OP {self.ordem_id}"


class ConsumosProducao(models.Model):
    ordem = models.ForeignKey('OrdensProducao', on_delete=models.CASCADE, related_name='consumos')
    produto = models.ForeignKey('Produtos', on_delete=models.PROTECT)
    local_id = models.ForeignKey('LocaisEstoque', on_delete=models.PROTECT, null=True, blank=True)
    quantidade = models.DecimalField(max_digits=15, decimal_places=4, default=Decimal('0.0000'))
    data_consumo = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'consumos_producao'
        ordering = ['-data_consumo']
        indexes = [
            models.Index(fields=['produto']),
        ]

    def __str__(self):
        return f"Consumo {self.ordem_id} - {self.produto_id}"


class ApontamentosProducao(models.Model):
    ordem = models.ForeignKey('OrdensProducao', on_delete=models.CASCADE, related_name='apontamentos')
    local_id = models.ForeignKey('LocaisEstoque', on_delete=models.PROTECT, null=True, blank=True)
    quantidade = models.DecimalField(max_digits=15, decimal_places=4, default=Decimal('0.0000'))
    data_apontamento = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'apontamentos_producao'
        ordering = ['-data_apontamento']
        indexes = [
            models.Index(fields=['ordem']),
        ]

    def __str__(self):
        return f"Apontamento {self.ordem_id}"


class AtivosPatrimonio(models.Model):
    STATUS_CHOICES = [
        ('A', 'Ativo'),
        ('I', 'Inativo'),
        ('B', 'Baixado'),
    ]

    codigo = models.CharField(max_length=30, db_index=True)
    descricao = models.CharField(max_length=150)
    categoria = models.CharField(max_length=100, null=True, blank=True)
    localizacao = models.CharField(max_length=150, null=True, blank=True)
    data_aquisicao = models.DateField(null=True, blank=True)
    valor_aquisicao = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    vida_util_meses = models.IntegerField(null=True, blank=True)
    valor_residual = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')
    observacoes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'ativos_patrimonio'
        ordering = ['descricao']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.descricao}"


class ManutencoesAtivos(models.Model):
    STATUS_CHOICES = [
        ('A', 'Aberta'),
        ('E', 'Em execução'),
        ('F', 'Finalizada'),
        ('C', 'Cancelada'),
    ]

    ativo = models.ForeignKey('AtivosPatrimonio', on_delete=models.PROTECT, related_name='manutencoes')
    tipo = models.CharField(max_length=50)
    data_abertura = models.DateTimeField(null=True, blank=True)
    data_fechamento = models.DateTimeField(null=True, blank=True)
    responsavel_id = models.IntegerField(null=True, blank=True)
    custo_previsto = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    custo_real = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')
    observacoes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'manutencoes_ativos'
        ordering = ['-data_abertura']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['ativo']),
        ]

    def __str__(self):
        return f"Manutenção {self.id} - {self.ativo_id}"


class DepreciacoesAtivos(models.Model):
    ativo = models.ForeignKey('AtivosPatrimonio', on_delete=models.CASCADE, related_name='depreciacoes')
    competencia = models.DateField()
    valor_depreciado = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    valor_acumulado = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        db_table = 'depreciacoes_ativos'
        ordering = ['-competencia']
        indexes = [
            models.Index(fields=['ativo']),
            models.Index(fields=['competencia']),
        ]

    def __str__(self):
        return f"Depreciação {self.ativo_id} {self.competencia}"
class LocaisEstoque(models.Model):
    codigo = models.CharField(max_length=20)
    descricao = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, null=True, blank=True)
    endereco = models.CharField(max_length=100, null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)
    ativo = models.BooleanField(null=True, blank=True, default=True)

    class Meta:
        db_table = 'locais_estoque'

    def __str__(self):
        return f"{self.codigo} - {self.descricao}"

class Lotes(models.Model):
    produto_id = models.ForeignKey('Produtos', on_delete=models.PROTECT, null=True, blank=True)
    numero_lote = models.CharField(max_length=50)
    data_fabricacao = models.DateField(null=True, blank=True)
    data_validade = models.DateField(null=True, blank=True)
    quantidade_inicial = models.DecimalField(max_digits=10, decimal_places=3)
    quantidade_atual = models.DecimalField(max_digits=10, decimal_places=3)
    custo_unitario = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    nota_fiscal_entrada_id = models.ForeignKey('NotasFiscaisEntrada', on_delete=models.PROTECT, null=True, blank=True)
    fornecedor_id = models.ForeignKey('Fornecedores', on_delete=models.PROTECT, null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    ativo = models.BooleanField(null=True, blank=True, default=True)

    class Meta:
        db_table = 'lotes'

    def __str__(self):
        return f"Lote {self.numero_lote} - {self.produto_id}"

class Marcas(models.Model):
    nome = models.CharField(max_length=50)

    class Meta:
        db_table = 'marcas'

    def __str__(self):
        return self.nome
    
class NotasFiscaisSaida(models.Model):
    # Identificação
    numero_nota = models.CharField(
        max_length=20, 
        verbose_name='Número da NF',
        db_index=True
    )
    data = models.DateTimeField(
        verbose_name='Data',
        null=True,
        blank=True
    )
    cliente = models.ForeignKey(
        'Clientes',
        on_delete=models.PROTECT,
        related_name='notas_fiscais_saida',
        verbose_name='Cliente',
        null=True,
        blank=True
    )

    # Valores
    valor_produtos = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor dos Produtos',
        default=Decimal('0.00')
    )
    base_calculo = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Base de Cálculo',
        default=Decimal('0.00')
    )
    desconto = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Desconto',
        default=Decimal('0.00')
    )
    valor_frete = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor do Frete',
        default=Decimal('0.00')
    )
    tipo_frete = models.CharField(
        max_length=10,
        verbose_name='Tipo de Frete',
        null=True,
        blank=True
    )
    valor_icms = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor do ICMS',
        default=Decimal('0.00')
    )
    valor_ipi = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor do IPI',
        default=Decimal('0.00')
    )
    valor_icms_fonte = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor do ICMS Fonte',
        default=Decimal('0.00')
    )
    valor_total_nota = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor Total da Nota',
        default=Decimal('0.00')
    )
    imposto_federal_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Imposto Federal Total',
        default=Decimal('0.00')
    )
    outras_despesas = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Outras Despesas',
        default=Decimal('0.00')
    )
    seguro = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Seguro',
        default=Decimal('0.00')
    )

    # Informações de Pagamento
    forma_pagamento = models.CharField(
        max_length=50,
        verbose_name='Forma de Pagamento',
        null=True,
        blank=True
    )
    condicoes = models.CharField(
        max_length=100,
        verbose_name='Condições de Pagamento',
        null=True,
        blank=True
    )
    parcelas = models.CharField(
        max_length=100,
        verbose_name='Parcelas',
        null=True,
        blank=True
    )
    val_ref = models.CharField(
        max_length=50,
        verbose_name='Valor de Referência',
        null=True,
        blank=True
    )

    # Pessoas envolvidas
    vendedor = models.ForeignKey(
        'Funcionarios',
        on_delete=models.PROTECT,
        related_name='notas_fiscais_vendedor',
        verbose_name='Vendedor',
        null=True,
        blank=True
    )
    operador = models.CharField(
        max_length=100,
        verbose_name='Operador',
        null=True,
        blank=True
    )
    transportadora = models.ForeignKey(
        'Transportadoras',
        on_delete=models.PROTECT,
        related_name='notas_fiscais_saida',
        verbose_name='Transportadora',
        null=True,
        blank=True
    )

    # Informações de Transporte
    formulario = models.CharField(
        max_length=20,
        verbose_name='Formulário',
        null=True,
        blank=True
    )
    peso = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        verbose_name='Peso',
        null=True,
        blank=True,
        default=Decimal('0.000')
    )
    volume = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        verbose_name='Volume',
        null=True,
        blank=True,
        default=Decimal('0.000')
    )

    # Informações Fiscais
    operacao = models.CharField(
        max_length=50,
        verbose_name='Operação',
        null=True,
        blank=True
    )
    cfop = models.CharField(
        max_length=10,
        verbose_name='CFOP',
        null=True,
        blank=True
    )
    n_serie = models.CharField(
        max_length=10,
        verbose_name='Série',
        null=True,
        blank=True
    )
    percentual_icms = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Percentual de ICMS',
        null=True,
        blank=True,
        default=Decimal('0.00')
    )
    nf_referencia = models.CharField(
        max_length=50,
        verbose_name='NF Referência',
        null=True,
        blank=True
    )
    finalidade = models.CharField(
        max_length=50,
        verbose_name='Finalidade',
        null=True,
        blank=True
    )

    # Outros campos
    comissao = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Comissão',
        null=True,
        blank=True,
        default=Decimal('0.00')
    )
    obs = models.TextField(
        verbose_name='Observações',
        null=True,
        blank=True
    )
    detalhes = models.TextField(
        verbose_name='Detalhes',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'notas_fiscais_saida'
        verbose_name = 'Nota Fiscal de Saída'
        verbose_name_plural = 'Notas Fiscais de Saída'
        ordering = ['-data']
        indexes = [
            models.Index(fields=['numero_nota']),
            models.Index(fields=['data']),
            models.Index(fields=['cliente']),
            models.Index(fields=['vendedor']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['numero_nota', 'n_serie'],
                name='unique_nfs_numero_serie'
            )
        ]

    def __str__(self):
        return f"NFS {self.numero_nota} - {self.cliente}"

    def clean(self):
        # Calcula o valor total da nota
        self.valor_total_nota = (
            self.valor_produtos +
            self.valor_frete +
            self.valor_ipi +
            self.outras_despesas +
            self.seguro -
            self.desconto
        )
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
class ItensNfSaida(models.Model):
    nota_fiscal = models.ForeignKey(
        'NotasFiscaisSaida',
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='Nota Fiscal'
    )
    data = models.DateTimeField(
        verbose_name='Data',
        null=True,
        blank=True
    )
    produto = models.ForeignKey(
        'Produtos',
        on_delete=models.PROTECT,
        related_name='itens_nf_saida',
        verbose_name='Produto'
    )
    quantidade = models.DecimalField(
        max_digits=15, 
        decimal_places=4, 
        verbose_name='Quantidade',
        null=True,
        blank=True,
        default=Decimal('0.0000')
    )
    valor_unitario = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name='Valor Unitário',
        null=True,
        blank=True,
        default=Decimal('0.00')
    )
    valor_total = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name='Valor Total',
        null=True,
        blank=True,
        default=Decimal('0.00')
    )
    percentual_ipi = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name='Percentual IPI', 
        default=Decimal('0.00'),
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=50, 
        verbose_name='Status',
        null=True,
        blank=True
    )
    aliquota = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name='Alíquota', 
        default=Decimal('0.00'),
        null=True,
        blank=True
    )
    reducao = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name='Redução', 
        default=Decimal('0.00'),
        null=True,
        blank=True
    )
    desconto = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name='Desconto', 
        default=Decimal('0.00'),
        null=True,
        blank=True
    )
    cst_a = models.CharField(
        max_length=3, 
        verbose_name='CST A',
        null=True,
        blank=True
    )
    cst_b = models.CharField(
        max_length=3, 
        verbose_name='CST B',
        null=True,
        blank=True
    )
    controle = models.CharField(
        max_length=50, 
        verbose_name='Controle',
        null=True,
        blank=True
    )
    frete = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name='Frete', 
        default=Decimal('0.00'),
        null=True,
        blank=True
    )
    outras_despesas = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name='Outras Despesas',
        default=Decimal('0.00'),
        null=True,
        blank=True
    )
    seguro = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name='Seguro',
        default=Decimal('0.00'),
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'itens_nf_saida'
        verbose_name = 'Item da NFS'
        verbose_name_plural = 'Itens da NFS'
        ordering = ['nota_fiscal', 'id']
        indexes = [
            models.Index(fields=['nota_fiscal', 'produto']),
            models.Index(fields=['data']),
            models.Index(fields=['produto']),
        ]

    def __str__(self):
        return f"Item {self.id} - NF {self.nota_fiscal}"

    def clean(self):
        # Calcula o valor total do item
        if self.quantidade is not None and self.valor_unitario is not None:
            total = self.quantidade * self.valor_unitario
            
            # Adiciona outras despesas
            if self.frete:
                total += self.frete
            if self.outras_despesas:
                total += self.outras_despesas
            if self.seguro:
                total += self.seguro
            
            # Subtrai desconto
            if self.desconto:
                total -= self.desconto
                
            self.valor_total = total

        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class OrcamentosVenda(models.Model):
    STATUS_CHOICES = [
        ('ABERTO', 'Aberto'),
        ('APROVADO', 'Aprovado'),
        ('REJEITADO', 'Rejeitado'),
        ('EXPIRADO', 'Expirado'),
        ('CONVERTIDO', 'Convertido'),
    ]

    numero_orcamento = models.CharField(
        max_length=30,
        verbose_name='Número do Orçamento',
        null=True,
        blank=True
    )
    cliente = models.ForeignKey(
        'Clientes',
        on_delete=models.PROTECT,
        related_name='orcamentos_venda',
        verbose_name='Cliente',
        null=True,
        blank=True
    )
    vendedor = models.ForeignKey(
        'Funcionarios',
        on_delete=models.PROTECT,
        related_name='orcamentos_venda',
        verbose_name='Vendedor',
        null=True,
        blank=True
    )
    data_emissao = models.DateTimeField(
        verbose_name='Data de Emissão',
        null=True,
        blank=True
    )
    validade = models.DateField(
        verbose_name='Validade',
        null=True,
        blank=True
    )
    valor_produtos = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor dos Produtos',
        default=Decimal('0.00')
    )
    desconto = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Desconto',
        default=Decimal('0.00')
    )
    frete = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Frete',
        default=Decimal('0.00')
    )
    impostos = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Impostos',
        default=Decimal('0.00')
    )
    valor_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor Total',
        default=Decimal('0.00')
    )
    observacoes = models.TextField(
        verbose_name='Observações',
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ABERTO',
        verbose_name='Status'
    )

    class Meta:
        db_table = 'orcamentos_venda'
        verbose_name = 'Orçamento de Venda'
        verbose_name_plural = 'Orçamentos de Venda'
        ordering = ['-data_emissao', '-id']
        indexes = [
            models.Index(fields=['numero_orcamento']),
            models.Index(fields=['data_emissao']),
            models.Index(fields=['cliente']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Orçamento {self.numero_orcamento or self.id} - {self.cliente}"

    def clean(self):
        self.valor_total = (
            self.valor_produtos +
            self.frete +
            self.impostos -
            self.desconto
        )
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class ItensOrcamentoVenda(models.Model):
    orcamento = models.ForeignKey(
        'OrcamentosVenda',
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='Orçamento'
    )
    produto = models.ForeignKey(
        'Produtos',
        on_delete=models.PROTECT,
        related_name='itens_orcamento_venda',
        verbose_name='Produto'
    )
    quantidade = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        verbose_name='Quantidade',
        default=Decimal('0.0000')
    )
    valor_unitario = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor Unitário',
        default=Decimal('0.00')
    )
    desconto = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Desconto',
        default=Decimal('0.00')
    )
    valor_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor Total',
        default=Decimal('0.00')
    )

    class Meta:
        db_table = 'itens_orcamento_venda'
        verbose_name = 'Item do Orçamento'
        verbose_name_plural = 'Itens do Orçamento'
        ordering = ['orcamento', 'id']
        indexes = [
            models.Index(fields=['orcamento', 'produto']),
            models.Index(fields=['produto']),
        ]

    def __str__(self):
        return f"Item {self.id} - Orçamento {self.orcamento_id}"

    def clean(self):
        self.valor_total = (self.quantidade * self.valor_unitario) - (self.desconto or Decimal('0.00'))
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class PedidosVenda(models.Model):
    STATUS_CHOICES = [
        ('RASCUNHO', 'Rascunho'),
        ('APROVADO', 'Aprovado'),
        ('EXPEDIDO', 'Expedido'),
        ('FATURADO', 'Faturado'),
        ('CANCELADO', 'Cancelado'),
    ]

    numero_pedido = models.CharField(
        max_length=30,
        verbose_name='Número do Pedido',
        null=True,
        blank=True
    )
    cliente = models.ForeignKey(
        'Clientes',
        on_delete=models.PROTECT,
        related_name='pedidos_venda',
        verbose_name='Cliente',
        null=True,
        blank=True
    )
    vendedor = models.ForeignKey(
        'Funcionarios',
        on_delete=models.PROTECT,
        related_name='pedidos_venda',
        verbose_name='Vendedor',
        null=True,
        blank=True
    )
    orcamento = models.ForeignKey(
        'OrcamentosVenda',
        on_delete=models.SET_NULL,
        related_name='pedidos_venda',
        verbose_name='Orçamento',
        null=True,
        blank=True
    )
    data_emissao = models.DateTimeField(
        verbose_name='Data de Emissão',
        null=True,
        blank=True
    )
    data_aprovacao = models.DateTimeField(
        verbose_name='Data de Aprovação',
        null=True,
        blank=True
    )
    data_faturamento = models.DateTimeField(
        verbose_name='Data de Faturamento',
        null=True,
        blank=True
    )
    forma_pagamento = models.CharField(
        max_length=50,
        verbose_name='Forma de Pagamento',
        null=True,
        blank=True
    )
    condicoes_pagamento = models.CharField(
        max_length=100,
        verbose_name='Condições de Pagamento',
        null=True,
        blank=True
    )
    prazo_entrega = models.CharField(
        max_length=100,
        verbose_name='Prazo de Entrega',
        null=True,
        blank=True
    )
    valor_produtos = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor dos Produtos',
        default=Decimal('0.00')
    )
    desconto = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Desconto',
        default=Decimal('0.00')
    )
    frete = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Frete',
        default=Decimal('0.00')
    )
    impostos = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Impostos',
        default=Decimal('0.00')
    )
    valor_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor Total',
        default=Decimal('0.00')
    )
    observacoes = models.TextField(
        verbose_name='Observações',
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='RASCUNHO',
        verbose_name='Status'
    )

    class Meta:
        db_table = 'pedidos_venda'
        verbose_name = 'Pedido de Venda'
        verbose_name_plural = 'Pedidos de Venda'
        ordering = ['-data_emissao', '-id']
        indexes = [
            models.Index(fields=['numero_pedido']),
            models.Index(fields=['data_emissao']),
            models.Index(fields=['cliente']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Pedido {self.numero_pedido or self.id} - {self.cliente}"

    def clean(self):
        self.valor_total = (
            self.valor_produtos +
            self.frete +
            self.impostos -
            self.desconto
        )
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class ItensPedidoVenda(models.Model):
    pedido = models.ForeignKey(
        'PedidosVenda',
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='Pedido'
    )
    produto = models.ForeignKey(
        'Produtos',
        on_delete=models.PROTECT,
        related_name='itens_pedido_venda',
        verbose_name='Produto'
    )
    quantidade = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        verbose_name='Quantidade',
        default=Decimal('0.0000')
    )
    valor_unitario = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor Unitário',
        default=Decimal('0.00')
    )
    desconto = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Desconto',
        default=Decimal('0.00')
    )
    valor_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor Total',
        default=Decimal('0.00')
    )

    class Meta:
        db_table = 'itens_pedido_venda'
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'
        ordering = ['pedido', 'id']
        indexes = [
            models.Index(fields=['pedido', 'produto']),
            models.Index(fields=['produto']),
        ]

    def __str__(self):
        return f"Item {self.id} - Pedido {self.pedido_id}"

    def clean(self):
        self.valor_total = (self.quantidade * self.valor_unitario) - (self.desconto or Decimal('0.00'))
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class ComissoesVenda(models.Model):
    STATUS_CHOICES = [
        ('ABERTA', 'Aberta'),
        ('PAGA', 'Paga'),
        ('CANCELADA', 'Cancelada'),
    ]

    pedido = models.ForeignKey(
        'PedidosVenda',
        on_delete=models.CASCADE,
        related_name='comissoes',
        verbose_name='Pedido'
    )
    vendedor = models.ForeignKey(
        'Funcionarios',
        on_delete=models.PROTECT,
        related_name='comissoes_venda',
        verbose_name='Vendedor'
    )
    percentual = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name='Percentual',
        default=Decimal('0.00')
    )
    valor_base = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor Base',
        default=Decimal('0.00')
    )
    valor_comissao = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor Comissão',
        default=Decimal('0.00')
    )
    data_lancamento = models.DateTimeField(
        verbose_name='Data de Lançamento',
        null=True,
        blank=True
    )
    data_pagamento = models.DateTimeField(
        verbose_name='Data de Pagamento',
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ABERTA',
        verbose_name='Status'
    )

    class Meta:
        db_table = 'comissoes_venda'
        verbose_name = 'Comissão de Venda'
        verbose_name_plural = 'Comissões de Venda'
        ordering = ['-data_lancamento', '-id']
        indexes = [
            models.Index(fields=['pedido']),
            models.Index(fields=['vendedor']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Comissão {self.id} - Pedido {self.pedido_id}"

    def clean(self):
        if self.valor_base and self.percentual:
            self.valor_comissao = (self.valor_base * self.percentual) / Decimal('100.00')
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class NotasFiscaisServico(models.Model):
    # Identificação
    numero_nota = models.CharField(
        max_length=20, 
        verbose_name='Número da NF',
        db_index=True
    )
    mes_ano = models.CharField(
        max_length=7,
        verbose_name='Mês/Ano',
        null=True,
        blank=True
    )
    data = models.DateTimeField(
        verbose_name='Data',
        null=True,
        blank=True
    )
    cliente = models.ForeignKey(
        'Clientes',
        on_delete=models.PROTECT,
        related_name='notas_fiscais_servico',
        verbose_name='Cliente',
        null=True,
        blank=True
    )

    # Valores
    valor_produtos = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor dos Serviços',
        default=Decimal('0.00')
    )
    iss = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='ISS',
        default=Decimal('0.00')
    )
    base_calculo = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Base de Cálculo',
        default=Decimal('0.00')
    )
    desconto = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Desconto',
        default=Decimal('0.00')
    )
    valor_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Valor Total da Nota',
        default=Decimal('0.00')
    )

    # Informações de Pagamento
    forma_pagamento = models.CharField(
        max_length=50,
        verbose_name='Forma de Pagamento',
        null=True,
        blank=True
    )
    condicoes = models.CharField(
        max_length=100,
        verbose_name='Condições de Pagamento',
        null=True,
        blank=True
    )
    parcelas = models.CharField(
        max_length=100,
        verbose_name='Parcelas',
        null=True,
        blank=True
    )

    # Pessoas envolvidas
    vendedor = models.ForeignKey(
        'Funcionarios',
        on_delete=models.PROTECT,
        related_name='notas_fiscais_servico_vendedor',
        verbose_name='Vendedor',
        null=True,
        blank=True
    )
    operador = models.CharField(
        max_length=100,
        verbose_name='Operador',
        null=True,
        blank=True
    )
    transportadora = models.ForeignKey(
        'Transportadoras',
        on_delete=models.PROTECT,
        related_name='notas_fiscais_servico',
        verbose_name='Transportadora',
        null=True,
        blank=True
    )

    # Informações de Controle
    formulario = models.CharField(
        max_length=20,
        verbose_name='Formulário',
        null=True,
        blank=True
    )
    obs = models.TextField(
        verbose_name='Observações',
        null=True,
        blank=True
    )
    operacao = models.CharField(
        max_length=50,
        verbose_name='Operação',
        null=True,
        blank=True
    )
    cfop = models.CharField(
        max_length=10,
        verbose_name='CFOP',
        null=True,
        blank=True
    )
    n_serie = models.CharField(
        max_length=10,
        verbose_name='Número de Série',
        null=True,
        blank=True
    )
    comissao = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Comissão',
        null=True,
        blank=True,
        default=Decimal('0.00')
    )
    tipo = models.CharField(
        max_length=50,
        verbose_name='Tipo',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'notas_fiscais_servico'
        verbose_name = 'Nota Fiscal de Serviço'
        verbose_name_plural = 'Notas Fiscais de Serviço'
        ordering = ['-data']
        indexes = [
            models.Index(fields=['numero_nota']),
            models.Index(fields=['data']),
            models.Index(fields=['mes_ano']),
            models.Index(fields=['cliente']),
            models.Index(fields=['vendedor'])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['numero_nota', 'n_serie'],
                name='unique_nfserv_numero_serie'
            )
        ]

    def __str__(self):
        return f"NFS {self.numero_nota} - {self.cliente}"

    def clean(self):
        # Calcula o valor total da nota
        self.valor_total = (
            self.valor_produtos -
            self.desconto
        )
        
        # Calcula base de cálculo se não informada
        if not self.base_calculo:
            self.base_calculo = self.valor_total
            
        # Calcula ISS se base de cálculo existir (usando 5% como exemplo)
        if self.base_calculo and not self.iss:
            self.iss = self.base_calculo * Decimal('0.05')
            
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def valor_liquido(self):
        """Retorna o valor líquido (total - ISS)"""
        return self.valor_total - (self.iss or Decimal('0.00'))
    

class ItensNfServico(models.Model):
    nota_fiscal = models.ForeignKey(
        'NotasFiscaisServico',
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='Nota Fiscal'
    )
    data = models.DateTimeField(
        verbose_name='Data',
        null=True,
        blank=True
    )
    servico = models.CharField(
        max_length=240,
        verbose_name='Servico',
        null=True,
        blank=True
    )
    
    quantidade = models.DecimalField(
        max_digits=15, 
        decimal_places=4, 
        verbose_name='Quantidade',
        null=True,
        blank=True,
        default=Decimal('0.0000')
    )
    valor_unitario = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name='Valor Unitário',
        null=True,
        blank=True,
        default=Decimal('0.00')
    )
    valor_total = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name='Valor Total',
        null=True,
        blank=True,
        default=Decimal('0.00')
    )

    class Meta:
        db_table = 'itens_nf_servico'
        verbose_name = 'Item da NFS'
        verbose_name_plural = 'Itens da NFS'
        ordering = ['nota_fiscal', 'id']
        indexes = [
            models.Index(fields=['nota_fiscal', 'servico']),
            models.Index(fields=['data']),
            models.Index(fields=['servico']),
        ]

    def __str__(self):
        return f"Item {self.id} - NFS {self.nota_fiscal}"

    def clean(self):
        """Calcula o valor total do item"""
        if self.quantidade is not None and self.valor_unitario is not None:
            self.valor_total = self.quantidade * self.valor_unitario
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class EstoqueInicial(models.Model):
    """Modelo para armazenar o estoque inicial de 01/01/2025"""
    produto = models.ForeignKey('Produtos', on_delete=models.CASCADE)
    data_inicial = models.DateField(default='2025-01-01')
    quantidade_inicial = models.DecimalField(max_digits=10, decimal_places=3, default=0.0)
    valor_unitario_inicial = models.DecimalField(max_digits=10, decimal_places=4, default=0.0)
    valor_total_inicial = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    data_calculo = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'estoque_inicial'
        unique_together = ['produto', 'data_inicial']
        indexes = [
            models.Index(fields=['produto']),
            models.Index(fields=['data_inicial']),
        ]

    def __str__(self):
        return f"Estoque Inicial {self.produto.codigo} - {self.data_inicial}"

    def save(self, *args, **kwargs):
        if self.quantidade_inicial and self.valor_unitario_inicial:
            self.valor_total_inicial = self.quantidade_inicial * self.valor_unitario_inicial
        super().save(*args, **kwargs)


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
