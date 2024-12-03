from django.db import models

class Categorias(models.Model):
    codigo = models.IntegerField()
    nome = models.CharField(max_length=50)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True, default='CURRENT_TIMESTAMP')
    ativo = models.BooleanField( null=True, blank=True, default=True)

    class Meta:
        db_table = 'categorias'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class CategoriasProdutos(models.Model):
    nome = models.CharField(max_length=50)
    descricao = models.TextField( null=True, blank=True)
    ativo = models.BooleanField( null=True, blank=True, default=True)

    class Meta:
        db_table = 'categorias_produtos'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class Clientes(models.Model):
    tipo_pessoa = models.CharField(max_length=255)
    nome = models.CharField(max_length=100)
    cpf_cnpj = models.CharField(max_length=14)
    rg_ie = models.CharField(max_length=20, null=True, blank=True)
    data_nascimento = models.DateField( null=True, blank=True)
    endereco = models.CharField(max_length=100, null=True, blank=True)
    numero = models.CharField(max_length=10, null=True, blank=True)
    complemento = models.CharField(max_length=50, null=True, blank=True)
    bairro = models.CharField(max_length=50, null=True, blank=True)
    cidade = models.CharField(max_length=50, null=True, blank=True)
    estado = models.CharField(max_length=255, null=True, blank=True)
    cep = models.CharField(max_length=8, null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    limite_credito = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.0)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True, default='CURRENT_TIMESTAMP')
    ativo = models.BooleanField( null=True, blank=True, default=True)
    contato = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'clientes'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class ContagensInventario(models.Model):
    inventario_id = models.ForeignKey('Inventarios', on_delete=models.PROTECT, null=True, blank=True)
    produto_id = models.ForeignKey('Produtos', on_delete=models.PROTECT, null=True, blank=True)
    lote_id = models.ForeignKey('Lotes', on_delete=models.PROTECT, null=True, blank=True)
    quantidade_sistema = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    quantidade_contagem = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    divergencia = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    usuario_contagem_id = models.IntegerField( null=True, blank=True)
    data_contagem = models.DateTimeField( null=True, blank=True)
    observacoes = models.TextField( null=True, blank=True)

    class Meta:
        db_table = 'contagens_inventario'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class ContasPagar(models.Model):
    fornecedor_id = models.ForeignKey('Fornecedores', on_delete=models.PROTECT, null=True, blank=True)
    nota_fiscal_id = models.ForeignKey('NotasFiscaisCompra', on_delete=models.PROTECT, null=True, blank=True)
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateField()
    data_pagamento = models.DateField( null=True, blank=True)
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    juros = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    multa = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True)
    forma_pagamento = models.CharField(max_length=50, null=True, blank=True)
    observacoes = models.TextField( null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True, default='CURRENT_TIMESTAMP')

    class Meta:
        db_table = 'contas_pagar'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class ContasReceber(models.Model):
    cliente_id = models.ForeignKey('Clientes', on_delete=models.PROTECT, null=True, blank=True)
    nota_fiscal_id = models.ForeignKey('NotasFiscaisVenda', on_delete=models.PROTECT, null=True, blank=True)
    contrato_id = models.ForeignKey('ContratosLocacao', on_delete=models.PROTECT, null=True, blank=True)
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateField()
    data_recebimento = models.DateField( null=True, blank=True)
    valor_recebido = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    juros = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    multa = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True)
    forma_recebimento = models.CharField(max_length=50, null=True, blank=True)
    observacoes = models.TextField( null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True, default='CURRENT_TIMESTAMP')

    class Meta:
        db_table = 'contas_receber'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class ContratosLocacao(models.Model):
    cliente_id = models.ForeignKey('Clientes', on_delete=models.PROTECT, null=True, blank=True)
    contrato = models.CharField(max_length=100, null=True, blank=True)
    cliente = models.CharField(max_length=100, null=True, blank=True)
    tipocontrato = models.CharField(max_length=20, null=True, blank=True)
    renovado = models.CharField(max_length=100, null=True, blank=True)
    totalmaquinas = models.CharField(max_length=100, null=True, blank=True)
    valorcontrato = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    numeroparcelas = models.CharField(max_length=100, null=True, blank=True)
    valorpacela = models.CharField(max_length=100, null=True, blank=True)
    referencia = models.CharField(max_length=100, null=True, blank=True)
    data = models.CharField(max_length=100, null=True, blank=True)
    incio = models.CharField(max_length=100, null=True, blank=True)
    fim = models.CharField(max_length=100, null=True, blank=True)
    ultimoatendimento = models.CharField(max_length=100, null=True, blank=True)
    nmaquinas = models.CharField(max_length=100, null=True, blank=True)
    clientereal = models.CharField(max_length=100, null=True, blank=True)
    tipocontratoreal = models.CharField(max_length=100, null=True, blank=True)
    obs = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'contratos_locacao'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class CustosAdicionaisFrete(models.Model):
    frete_id = models.ForeignKey('Fretes', on_delete=models.PROTECT, null=True, blank=True)
    tipo_custo = models.CharField(max_length=50)
    descricao = models.TextField( null=True, blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True, default='CURRENT_TIMESTAMP')

    class Meta:
        db_table = 'custos_adicionais_frete'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class Despesas(models.Model):
    codigo = models.IntegerField()
    descricao = models.CharField(max_length=50)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True, default='CURRENT_TIMESTAMP')
    ativo = models.BooleanField( null=True, blank=True, default=True)

    class Meta:
        db_table = 'despesas'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

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
    estado = models.CharField(max_length=255, null=True, blank=True)
    cep = models.CharField(max_length=8, null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True, default='CURRENT_TIMESTAMP')
    ativo = models.BooleanField( null=True, blank=True, default=True)

    class Meta:
        db_table = 'empresas'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class Fornecedores(models.Model):
    tipo_pessoa = models.CharField(max_length=255)
    nome = models.CharField(max_length=100)
    cpf_cnpj = models.CharField(max_length=14)
    rg_ie = models.CharField(max_length=20, null=True, blank=True)
    endereco = models.CharField(max_length=100, null=True, blank=True)
    numero = models.CharField(max_length=10, null=True, blank=True)
    complemento = models.CharField(max_length=50, null=True, blank=True)
    bairro = models.CharField(max_length=50, null=True, blank=True)
    cidade = models.CharField(max_length=50, null=True, blank=True)
    estado = models.CharField(max_length=255, null=True, blank=True)
    cep = models.CharField(max_length=11, null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    contato_nome = models.CharField(max_length=100, null=True, blank=True)
    contato_telefone = models.CharField(max_length=20, null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True, default='CURRENT_TIMESTAMP')
    ativo = models.BooleanField(null=True, blank=True, default=True)

    class Meta:
        db_table = 'fornecedores'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class Fretes(models.Model):
    tipo_operacao = models.CharField(max_length=20)
    transportadora_id = models.ForeignKey('Transportadoras', on_delete=models.PROTECT, null=True, blank=True)
    nota_fiscal_compra_id = models.ForeignKey('NotasFiscaisCompra', on_delete=models.PROTECT, null=True, blank=True)
    nota_fiscal_venda_id = models.ForeignKey('NotasFiscaisVenda', on_delete=models.PROTECT, null=True, blank=True)
    data_emissao = models.DateField()
    previsao_entrega = models.DateField( null=True, blank=True)
    data_entrega = models.DateField( null=True, blank=True)
    conhecimento_transporte = models.CharField(max_length=50, null=True, blank=True)
    codigo_rastreamento = models.CharField(max_length=50, null=True, blank=True)
    valor_frete = models.DecimalField(max_digits=10, decimal_places=2)
    valor_seguro = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_outros = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    peso_real = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    peso_cubado = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    volumes = models.IntegerField( null=True, blank=True)
    especie_volumes = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True)
    observacoes = models.TextField( null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True, default='CURRENT_TIMESTAMP')

    class Meta:
        db_table = 'fretes'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class Funcionarios(models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=11)
    rg = models.CharField(max_length=20, null=True, blank=True)
    data_nascimento = models.DateField( null=True, blank=True)
    data_admissao = models.DateField()
    data_demissao = models.DateField( null=True, blank=True)
    cargo = models.CharField(max_length=50, null=True, blank=True)
    salario_base = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    endereco = models.CharField(max_length=100, null=True, blank=True)
    numero = models.CharField(max_length=10, null=True, blank=True)
    complemento = models.CharField(max_length=50, null=True, blank=True)
    bairro = models.CharField(max_length=50, null=True, blank=True)
    cidade = models.CharField(max_length=50, null=True, blank=True)
    estado = models.CharField(max_length=255, null=True, blank=True)
    cep = models.CharField(max_length=8, null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    banco = models.CharField(max_length=50, null=True, blank=True)
    agencia = models.CharField(max_length=10, null=True, blank=True)
    conta = models.CharField(max_length=20, null=True, blank=True)
    pix = models.CharField(max_length=100, null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True, default='CURRENT_TIMESTAMP')
    ativo = models.BooleanField( null=True, blank=True, default=True)

    class Meta:
        db_table = 'funcionarios'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class Grupos(models.Model):
    codigo = models.IntegerField()
    nome = models.CharField(max_length=50)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True, default='CURRENT_TIMESTAMP')
    ativo = models.BooleanField( null=True, blank=True, default=True)

    class Meta:
        db_table = 'grupos'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class HistoricoRastreamento(models.Model):
    frete_id = models.ForeignKey('Fretes', on_delete=models.PROTECT, null=True, blank=True)
    data_evento = models.DateTimeField()
    status = models.CharField(max_length=50)
    localizacao = models.CharField(max_length=100, null=True, blank=True)
    descricao = models.TextField( null=True, blank=True)
    data_consulta = models.DateTimeField( null=True, blank=True, default='CURRENT_TIMESTAMP')

    class Meta:
        db_table = 'historico_rastreamento'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class Inventarios(models.Model):
    codigo = models.CharField(max_length=20)
    data_inicio = models.DateField()
    data_fim = models.DateField( null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True)
    tipo = models.CharField(max_length=20, null=True, blank=True)
    local_id = models.ForeignKey('LocaisEstoque', on_delete=models.PROTECT, null=True, blank=True)
    observacoes = models.TextField( null=True, blank=True)
    usuario_abertura_id = models.IntegerField( null=True, blank=True)
    usuario_fechamento_id = models.IntegerField( null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True, default='CURRENT_TIMESTAMP')

    class Meta:
        db_table = 'inventarios'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class ItensContratoLocacao(models.Model):
    contrato_id = models.ForeignKey('ContratosLocacao', on_delete=models.PROTECT, null=True, blank=True)
    produto_id = models.ForeignKey('Produtos', on_delete=models.PROTECT, null=True, blank=True)
    quantidade = models.IntegerField( null=True, blank=True)
    valor_diaria = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dias_locacao = models.IntegerField( null=True, blank=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    numeroserie = models.CharField(max_length=30, null=True, blank=True)
    categoria_id = models.ForeignKey('Categorias', on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        db_table = 'itens_contrato_locacao'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class ItensNfCompra(models.Model):
    nota_fiscal_id = models.ForeignKey('NotasFiscaisCompra', on_delete=models.PROTECT, null=True, blank=True)
    produto_id = models.ForeignKey('Produtos', on_delete=models.PROTECT, null=True, blank=True)
    quantidade = models.DecimalField(max_digits=10, decimal_places=3)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    valor_icms = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_ipi = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'itens_nf_compra'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class ItensNfVenda(models.Model):
    nota_fiscal_id = models.ForeignKey('NotasFiscaisVenda', on_delete=models.PROTECT, null=True, blank=True)
    produto_id = models.ForeignKey('Produtos', on_delete=models.PROTECT, null=True, blank=True)
    quantidade = models.DecimalField(max_digits=10, decimal_places=3)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    valor_icms = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_ipi = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'itens_nf_venda'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class LocaisEstoque(models.Model):
    codigo = models.CharField(max_length=20)
    descricao = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, null=True, blank=True)
    endereco = models.CharField(max_length=100, null=True, blank=True)
    observacoes = models.TextField( null=True, blank=True)
    ativo = models.BooleanField( null=True, blank=True, default=True)

    class Meta:
        db_table = 'locais_estoque'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class Lotes(models.Model):
    produto_id = models.ForeignKey('Produtos', on_delete=models.PROTECT, null=True, blank=True)
    numero_lote = models.CharField(max_length=50)
    data_fabricacao = models.DateField( null=True, blank=True)
    data_validade = models.DateField( null=True, blank=True)
    quantidade_inicial = models.DecimalField(max_digits=10, decimal_places=3)
    quantidade_atual = models.DecimalField(max_digits=10, decimal_places=3)
    custo_unitario = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    nota_fiscal_compra_id = models.ForeignKey('NotasFiscaisCompra', on_delete=models.PROTECT, null=True, blank=True)
    fornecedor_id = models.ForeignKey('Fornecedores', on_delete=models.PROTECT, null=True, blank=True)
    observacoes = models.TextField( null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True, default='CURRENT_TIMESTAMP')
    ativo = models.BooleanField( null=True, blank=True, default=True)

    class Meta:
        db_table = 'lotes'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class Marcas(models.Model):
    codigo = models.IntegerField()
    nome = models.CharField(max_length=50)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True, default='CURRENT_TIMESTAMP')
    ativo = models.BooleanField( null=True, blank=True, default=True)

    class Meta:
        db_table = 'marcas'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class MovimentacoesEstoque(models.Model):
    data_movimentacao = models.DateTimeField( default='CURRENT_TIMESTAMP')
    tipo_movimentacao_id = models.ForeignKey('TiposMovimentacaoEstoque', on_delete=models.PROTECT, null=True, blank=True)
    produto_id = models.ForeignKey('Produtos', on_delete=models.PROTECT, null=True, blank=True)
    lote_id = models.ForeignKey('Lotes', on_delete=models.PROTECT, null=True, blank=True)
    local_origem_id = models.ForeignKey('LocaisEstoque', on_delete=models.PROTECT, null=True, blank=True)
    local_destino_id = models.ForeignKey('LocaisEstoque', on_delete=models.PROTECT, null=True, blank=True)
    quantidade = models.DecimalField(max_digits=10, decimal_places=3)
    custo_unitario = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    nota_fiscal_compra_id = models.ForeignKey('NotasFiscaisCompra', on_delete=models.PROTECT, null=True, blank=True)
    nota_fiscal_venda_id = models.ForeignKey('NotasFiscaisVenda', on_delete=models.PROTECT, null=True, blank=True)
    usuario_id = models.IntegerField( null=True, blank=True)
    observacoes = models.TextField( null=True, blank=True)
    documento_referencia = models.CharField(max_length=50, null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True, default='CURRENT_TIMESTAMP')

    class Meta:
        db_table = 'movimentacoes_estoque'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class NotasFiscaisCompra(models.Model):
    fornecedor_id = models.ForeignKey('Fornecedores', on_delete=models.PROTECT, null=True, blank=True)
    numero_nota = models.CharField(max_length=20)
    serie_nota = models.CharField(max_length=5, null=True, blank=True)
    data_emissao = models.DateField()
    data_entrada = models.DateField()
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    valor_icms = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_ipi = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_frete = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    observacoes = models.TextField( null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True, default='CURRENT_TIMESTAMP')
    transportadora_id = models.ForeignKey('Transportadoras', on_delete=models.PROTECT, null=True, blank=True)
    frete_id = models.ForeignKey('Fretes', on_delete=models.PROTECT, null=True, blank=True)
    modalidade_frete = models.CharField(max_length=255, null=True, blank=True)
    peso_total = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    volumes = models.IntegerField( null=True, blank=True)
    especie_volumes = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'notas_fiscais_compra'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class NotasFiscaisVenda(models.Model):
    cliente_id = models.ForeignKey('Clientes', on_delete=models.PROTECT, null=True, blank=True)
    numero_nota = models.CharField(max_length=20)
    serie_nota = models.CharField(max_length=5, null=True, blank=True)
    data_emissao = models.DateField()
    data_saida = models.DateField()
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    valor_icms = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_ipi = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_frete = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    observacoes = models.TextField( null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True, default='CURRENT_TIMESTAMP')
    transportadora_id = models.ForeignKey('Transportadoras', on_delete=models.PROTECT, null=True, blank=True)
    frete_id = models.ForeignKey('Fretes', on_delete=models.PROTECT, null=True, blank=True)
    modalidade_frete = models.CharField(max_length=255, null=True, blank=True)
    peso_total = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    volumes = models.IntegerField( null=True, blank=True)
    especie_volumes = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'notas_fiscais_venda'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class OcorrenciasFrete(models.Model):
    frete_id = models.ForeignKey('Fretes', on_delete=models.PROTECT, null=True, blank=True)
    data_ocorrencia = models.DateTimeField()
    tipo_ocorrencia = models.CharField(max_length=50)
    descricao = models.TextField( null=True, blank=True)
    local_ocorrencia = models.CharField(max_length=100, null=True, blank=True)
    responsavel = models.CharField(max_length=100, null=True, blank=True)
    observacoes = models.TextField( null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True, default='CURRENT_TIMESTAMP')

    class Meta:
        db_table = 'ocorrencias_frete'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

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
    data_pagamento = models.DateField( null=True, blank=True)
    observacoes = models.TextField( null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True, default='CURRENT_TIMESTAMP')

    class Meta:
        db_table = 'pagamentos_funcionarios'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class PosicoesEstoque(models.Model):
    local_id = models.ForeignKey('LocaisEstoque', on_delete=models.PROTECT, null=True, blank=True)
    codigo = models.CharField(max_length=20)
    descricao = models.CharField(max_length=100, null=True, blank=True)
    ativo = models.BooleanField( null=True, blank=True, default=True)

    class Meta:
        db_table = 'posicoes_estoque'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class Produtos(models.Model):
    codigo = models.CharField(max_length=20)
    nome = models.CharField(max_length=100)
    descricao = models.TextField( null=True, blank=True)
    grupo_id = models.IntegerField( null=True, blank=True)
    unidade_medida = models.CharField(max_length=10, null=True, blank=True)
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    margem_lucro = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    estoque_minimo = models.IntegerField( null=True, blank=True)
    estoque_atual = models.IntegerField( null=True, blank=True, default='0')
    disponivel_locacao = models.BooleanField( null=True, blank=True, default=False)
    valor_locacao_diaria = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True, default='CURRENT_TIMESTAMP')
    ativo = models.BooleanField( null=True, blank=True, default=True)
    controla_lote = models.BooleanField( null=True, blank=True, default=False)
    controla_validade = models.BooleanField( null=True, blank=True, default=False)
    localizacao_padrao_id = models.ForeignKey('PosicoesEstoque', on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        db_table = 'produtos'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class RegioesEntrega(models.Model):
    transportadora_id = models.ForeignKey('Transportadoras', on_delete=models.PROTECT, null=True, blank=True)
    descricao = models.CharField(max_length=100)
    cep_inicial = models.CharField(max_length=8, null=True, blank=True)
    cep_final = models.CharField(max_length=8, null=True, blank=True)
    prazo_entrega = models.IntegerField( null=True, blank=True)
    valor_base = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_kg_adicional = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_seguro_percentual = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    observacoes = models.TextField( null=True, blank=True)
    ativo = models.BooleanField( null=True, blank=True, default=True)

    class Meta:
        db_table = 'regioes_entrega'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class SaldosEstoque(models.Model):
    produto_id = models.ForeignKey('Produtos', on_delete=models.PROTECT, null=True, blank=True)
    local_id = models.ForeignKey('LocaisEstoque', on_delete=models.PROTECT, null=True, blank=True)
    lote_id = models.ForeignKey('Lotes', on_delete=models.PROTECT, null=True, blank=True)
    quantidade = models.DecimalField(max_digits=10, decimal_places=3, default=0.0)
    quantidade_reservada = models.DecimalField(max_digits=10, decimal_places=3, default=0.0)
    custo_medio = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    ultima_movimentacao = models.DateTimeField( null=True, blank=True)

    class Meta:
        db_table = 'saldos_estoque'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class TabelasFrete(models.Model):
    transportadora_id = models.ForeignKey('Transportadoras', on_delete=models.PROTECT, null=True, blank=True)
    descricao = models.CharField(max_length=100)
    data_inicio_vigencia = models.DateField()
    data_fim_vigencia = models.DateField( null=True, blank=True)
    percentual_desconto = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    observacoes = models.TextField( null=True, blank=True)
    ativo = models.BooleanField( null=True, blank=True, default=True)

    class Meta:
        db_table = 'tabelas_frete'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

class TiposMovimentacaoEstoque(models.Model):
    codigo = models.CharField(max_length=10)
    descricao = models.CharField(max_length=50)
    tipo = models.CharField(max_length=255)
    movimenta_custo = models.BooleanField( null=True, blank=True, default=True)
    ativo = models.BooleanField( null=True, blank=True, default=True)

    class Meta:
        db_table = 'tipos_movimentacao_estoque'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

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
    estado = models.CharField(max_length=255, null=True, blank=True)
    cep = models.CharField(max_length=15, null=True, blank=True)
    fone = models.CharField(max_length=20, null=True, blank=True)
    celular = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    contato_principal = models.CharField(max_length=100, null=True, blank=True)
    site_rastreamento = models.CharField(max_length=200, null=True, blank=True)
    formato_codigo_rastreio = models.CharField(max_length=50, null=True, blank=True)
    prazo_medio_entrega = models.IntegerField( null=True, blank=True)
    valor_minimo_frete = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    percentual_seguro = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    observacoes = models.TextField( null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True, default='CURRENT_TIMESTAMP')
    ativo = models.BooleanField( null=True, blank=True, default=True)
    contato = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'transportadoras'

    def __str__(self):
        if hasattr(self, 'nome'):
            return str(self.nome)
        if hasattr(self, 'descricao'):
            return str(self.descricao)
        return str(self.id)

