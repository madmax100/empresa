# empresa/contas/models/fluxo_caixa.py
from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal

from contas.managers.fluxo_caixa import FluxoCaixaLancamentoManager

class FluxoCaixaLancamento(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída')
    ]
    
    CATEGORIA_CHOICES = [
        ('vendas', 'Vendas'),
        ('aluguel', 'Aluguel'),
        ('servicos', 'Serviços'),
        ('compra', 'Compra'),
        ('devolucao', 'Devolução'),
        ('comodato', 'Comodato'),
        ('simplesRemessa', 'Simples Remessa'),
        ('adiantamento', 'Adiantamento'),
    ]

    SUBCATEGORIA_CHOICES = [
        ('suprimentos', 'Suprimentos'),
        ('maquinas', 'Máquinas'),
        ('despesas_operacionais', 'Despesas Operacionais'),
        ('despesas_administrativas', 'Despesas Administrativas'),
        ('impostos', 'Impostos'),
        ('locacao_maquinas', 'Locação de Máquinas'),  # Novo
        ('manutencao', 'Manutenção'),                 # Novo
        ('folha_pagamento', 'Folha de Pagamento'),    # Novo
        ('outros', 'Outros')
    ]
    
    FONTE_CHOICES = [
        ('contrato', 'Contrato'),
        ('conta_receber', 'Conta a Receber'), 
        ('conta_pagar', 'Conta a Pagar'),
        ('nfe', 'Nota Fiscal de Entrada'),      # Novo
        ('nfs', 'Nota Fiscal de Saída'),        # Novo
        ('nfserv', 'Nota Fiscal de Serviço'),   # Novo
        ('estorno', 'Estorno'),
        ('outro', 'Outro')
    ]

    data = models.DateField(verbose_name='Data')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    valor = models.DecimalField(max_digits=15, decimal_places=2)
    realizado = models.BooleanField(default=False)
    descricao = models.CharField(max_length=200)
    categoria = models.CharField(max_length=50, choices=CATEGORIA_CHOICES)
    subcategoria = models.CharField(max_length=50, choices=SUBCATEGORIA_CHOICES)

    
    fonte_tipo = models.CharField(max_length=20, choices=FONTE_CHOICES)
    fonte_id = models.IntegerField(null=True, blank=True)
    
    data_realizacao = models.DateTimeField(null=True, blank=True)
    data_estorno = models.DateTimeField(null=True, blank=True)
    lancamento_estornado = models.ForeignKey(
        'self', 
        null=True, 
        blank=True,
        on_delete=models.SET_NULL,
        related_name='estornos'
    )
    
    cliente = models.ForeignKey(
        'Clientes',
        null=True,
        blank=True, 
        on_delete=models.PROTECT,
        related_name='lancamentos_fluxo'
    )

    fornecedor = models.ForeignKey(
        'Fornecedores',
        null=True,
        blank=True, 
        on_delete=models.PROTECT,
        related_name='lancamentos_fluxo'
    )
    
    conta_bancaria = models.ForeignKey(
        'ContasBancarias',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='lancamentos_fluxo'
    )
    
    observacoes = models.TextField(null=True, blank=True)
    objects = FluxoCaixaLancamentoManager()


    
    class Meta:
        db_table = 'fluxo_caixa_lancamentos'
        verbose_name = 'Lançamento do Fluxo de Caixa'
        verbose_name_plural = 'Lançamentos do Fluxo de Caixa'
        ordering = ['-data', 'tipo']
        indexes = [
            models.Index(fields=['data']),
            models.Index(fields=['tipo']),
            models.Index(fields=['categoria']),
            models.Index(fields=['fonte_tipo', 'fonte_id']),
            models.Index(fields=['realizado']),
            models.Index(fields=['cliente'])
        ]

    def clean(self):
        if self.data_realizacao and self.data_realizacao.date() < self.data:
            raise ValidationError('Data de realização não pode ser anterior à data do lançamento')
            
        if self.data_estorno and not self.lancamento_estornado:
            raise ValidationError('Lançamento estornado deve ser informado quando há data de estorno')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def valor_atualizado(self):
        """Retorna o valor considerando estornos"""
        if self.data_estorno:
            return Decimal('0.00')
        return self.valor
        
    @property
    def status(self):
        """Retorna o status do lançamento"""
        if self.data_estorno:
            return 'Estornado'
        if self.realizado:
            return 'Realizado'
        return 'Pendente'

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.descricao} ({self.data})"

class SaldoDiario(models.Model):
    """
    Modelo para controle de saldos diários
    """
    data = models.DateField(
        unique=True,
        verbose_name='Data'
    )
    saldo_inicial = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Saldo Inicial'
    )
    total_entradas = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        verbose_name='Total de Entradas'
    )
    total_saidas = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        verbose_name='Total de Saídas'
    )
    saldo_final = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Saldo Final'
    )
    
    # Valores Realizados vs Previstos
    total_entradas_realizadas = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        verbose_name='Total de Entradas Realizadas'
    )
    total_saidas_realizadas = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        verbose_name='Total de Saídas Realizadas'
    )
    total_entradas_previstas = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        verbose_name='Total de Entradas Previstas'
    )
    total_saidas_previstas = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        verbose_name='Total de Saídas Previstas'
    )
    
    # Controle de processamento
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name='Data de Atualização'
    )
    processado = models.BooleanField(
        default=False,
        verbose_name='Processado'
    )
    
    class Meta:
        db_table = 'saldos_diarios'
        verbose_name = 'Saldo Diário'
        verbose_name_plural = 'Saldos Diários'
        ordering = ['-data']
        indexes = [
            models.Index(fields=['data']),
            models.Index(fields=['processado']),
        ]

    def atualizar_totais(self):
        """Atualiza os totais baseado nos lançamentos do dia"""
        lancamentos = FluxoCaixaLancamento.objects.filter(data=self.data)
        
        self.total_entradas = sum(l.valor_atualizado for l in lancamentos if l.tipo == 'entrada')
        self.total_saidas = sum(l.valor_atualizado for l in lancamentos if l.tipo == 'saida')
        
        self.total_entradas_realizadas = sum(l.valor_atualizado for l in lancamentos if l.tipo == 'entrada' and l.realizado)
        self.total_saidas_realizadas = sum(l.valor_atualizado for l in lancamentos if l.tipo == 'saida' and l.realizado)
        
        self.total_entradas_previstas = self.total_entradas - self.total_entradas_realizadas
        self.total_saidas_previstas = self.total_saidas - self.total_saidas_realizadas
        
        self.saldo_final = self.saldo_inicial + self.total_entradas - self.total_saidas
        self.processado = True
        
    def save(self, *args, **kwargs):
        if not self.processado:
            self.atualizar_totais()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"Saldo do dia {self.data}"

class ConfiguracaoFluxoCaixa(models.Model):
    """
    Configurações gerais do fluxo de caixa
    """
    saldo_inicial = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        verbose_name='Saldo Inicial'
    )
    data_inicial_controle = models.DateField(
        verbose_name='Data Inicial de Controle'
    )
    dias_previsao = models.IntegerField(
        default=90,
        verbose_name='Dias de Previsão'
    )
    categorias = models.JSONField(
        default=list,
        verbose_name='Categorias Disponíveis'
    )
    
    # Flags de controle
    considerar_previsoes = models.BooleanField(
        default=True,
        verbose_name='Considerar Previsões'
    )
    alerta_saldo_negativo = models.BooleanField(
        default=True,
        verbose_name='Alerta de Saldo Negativo'
    )
    saldo_minimo_alerta = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        verbose_name='Saldo Mínimo para Alerta'
    )
    
    # Integrações
    sincronizar_contas = models.BooleanField(
        default=True,
        verbose_name='Sincronizar com Contas'
    )
    sincronizar_contratos = models.BooleanField(
        default=True,
        verbose_name='Sincronizar com Contratos'
    )
    
    class Meta:
        db_table = 'configuracoes_fluxo_caixa'
        verbose_name = 'Configuração do Fluxo de Caixa'
        verbose_name_plural = 'Configurações do Fluxo de Caixa'

    def clean(self):
        # Garantir que existe apenas uma configuração
        if not self.pk and ConfiguracaoFluxoCaixa.objects.exists():
            raise ValidationError('Só pode existir uma configuração de fluxo de caixa')
            
        # Validar categorias
        categorias_validas = [cat[0] for cat in FluxoCaixaLancamento.CATEGORIA_CHOICES]
        for categoria in self.categorias:
            if categoria not in categorias_validas:
                raise ValidationError(f'Categoria inválida: {categoria}')
                
    @classmethod
    def get_instance(cls):
        """Retorna a instância única de configuração"""
        return cls.objects.first()