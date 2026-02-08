from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contas', '0014_clientes_especificacao'),
    ]

    operations = [
        migrations.CreateModel(
            name='CentroCusto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=30, unique=True)),
                ('nome', models.CharField(max_length=255)),
                ('ativo', models.BooleanField(default=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Centro de Custo',
                'verbose_name_plural': 'Centros de Custo',
                'ordering': ['codigo'],
            },
        ),
        migrations.CreateModel(
            name='LancamentoContabil',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField()),
                ('descricao', models.CharField(max_length=255)),
                ('origem', models.CharField(choices=[('manual', 'Manual'), ('financeiro', 'Financeiro'), ('estoque', 'Estoque'), ('vendas', 'Vendas'), ('compras', 'Compras')], default='manual', max_length=20)),
                ('documento_ref', models.CharField(blank=True, max_length=100)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Lançamento Contábil',
                'verbose_name_plural': 'Lançamentos Contábeis',
                'ordering': ['-data', '-id'],
            },
        ),
        migrations.CreateModel(
            name='PeriodoContabil',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ano', models.PositiveSmallIntegerField()),
                ('mes', models.PositiveSmallIntegerField()),
                ('status', models.CharField(choices=[('aberto', 'Aberto'), ('fechado', 'Fechado')], default='aberto', max_length=10)),
                ('fechado_em', models.DateTimeField(blank=True, null=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Período Contábil',
                'verbose_name_plural': 'Períodos Contábeis',
                'ordering': ['-ano', '-mes'],
                'unique_together': {('ano', 'mes')},
            },
        ),
        migrations.CreateModel(
            name='PlanoContas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=30, unique=True)),
                ('nome', models.CharField(max_length=255)),
                ('tipo', models.CharField(choices=[('ativo', 'Ativo'), ('passivo', 'Passivo'), ('patrimonio', 'Patrimônio Líquido'), ('receita', 'Receita'), ('despesa', 'Despesa')], max_length=20)),
                ('natureza', models.CharField(choices=[('devedora', 'Devedora'), ('credora', 'Credora')], max_length=20)),
                ('nivel', models.PositiveSmallIntegerField(default=1)),
                ('ativa', models.BooleanField(default=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('conta_pai', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='subcontas', to='contas.planocontas')),
            ],
            options={
                'verbose_name': 'Plano de Contas',
                'verbose_name_plural': 'Plano de Contas',
                'ordering': ['codigo'],
            },
        ),
        migrations.CreateModel(
            name='ItemLancamentoContabil',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('D', 'Débito'), ('C', 'Crédito')], max_length=1)),
                ('valor', models.DecimalField(decimal_places=2, max_digits=15)),
                ('historico', models.CharField(blank=True, max_length=255)),
                ('centro_custo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='itens_lancamento', to='contas.centrocusto')),
                ('conta', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='itens_lancamento', to='contas.planocontas')),
                ('lancamento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens', to='contas.lancamentocontabil')),
            ],
            options={
                'verbose_name': 'Item de Lançamento Contábil',
                'verbose_name_plural': 'Itens de Lançamento Contábil',
                'ordering': ['id'],
            },
        ),
    ]
