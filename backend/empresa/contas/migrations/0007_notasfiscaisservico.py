# Generated by Django 5.1.3 on 2024-11-20 09:09

import django.db.models.deletion
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contas', '0006_remove_notasfiscaisconsumo_fornecedor_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotasFiscaisServico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_nota', models.CharField(db_index=True, max_length=20, verbose_name='Número da NF')),
                ('mes_ano', models.CharField(blank=True, max_length=7, null=True, verbose_name='Mês/Ano')),
                ('data', models.DateTimeField(blank=True, null=True, verbose_name='Data')),
                ('valor_produtos', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15, verbose_name='Valor dos Serviços')),
                ('iss', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15, verbose_name='ISS')),
                ('base_calculo', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15, verbose_name='Base de Cálculo')),
                ('desconto', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15, verbose_name='Desconto')),
                ('valor_total', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15, verbose_name='Valor Total da Nota')),
                ('forma_pagamento', models.CharField(blank=True, max_length=50, null=True, verbose_name='Forma de Pagamento')),
                ('condicoes', models.CharField(blank=True, max_length=100, null=True, verbose_name='Condições de Pagamento')),
                ('parcelas', models.CharField(blank=True, max_length=100, null=True, verbose_name='Parcelas')),
                ('operador', models.CharField(blank=True, max_length=100, null=True, verbose_name='Operador')),
                ('formulario', models.CharField(blank=True, max_length=20, null=True, verbose_name='Formulário')),
                ('obs', models.TextField(blank=True, null=True, verbose_name='Observações')),
                ('operacao', models.CharField(blank=True, max_length=50, null=True, verbose_name='Operação')),
                ('cfop', models.CharField(blank=True, max_length=5, null=True, verbose_name='CFOP')),
                ('n_serie', models.CharField(blank=True, max_length=5, null=True, verbose_name='Número de Série')),
                ('comissao', models.DecimalField(blank=True, decimal_places=2, default=Decimal('0.00'), max_digits=5, null=True, verbose_name='Comissão')),
                ('tipo', models.CharField(blank=True, max_length=50, null=True, verbose_name='Tipo')),
                ('cliente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='notas_fiscais_servico', to='contas.clientes', verbose_name='Cliente')),
                ('transportadora', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='notas_fiscais_servico', to='contas.transportadoras', verbose_name='Transportadora')),
                ('vendedor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='notas_fiscais_servico_vendedor', to='contas.funcionarios', verbose_name='Vendedor')),
            ],
            options={
                'verbose_name': 'Nota Fiscal de Serviço',
                'verbose_name_plural': 'Notas Fiscais de Serviço',
                'db_table': 'notas_fiscais_servico',
                'ordering': ['-data'],
                'indexes': [models.Index(fields=['numero_nota'], name='notas_fisca_numero__5fb581_idx'), models.Index(fields=['data'], name='notas_fisca_data_d39cb5_idx'), models.Index(fields=['mes_ano'], name='notas_fisca_mes_ano_6508e2_idx'), models.Index(fields=['cliente'], name='notas_fisca_cliente_b481aa_idx'), models.Index(fields=['vendedor'], name='notas_fisca_vendedo_762d6e_idx')],
                'constraints': [models.UniqueConstraint(fields=('numero_nota', 'n_serie'), name='unique_nfserv_numero_serie')],
            },
        ),
    ]