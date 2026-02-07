from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ContaPagar",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("descricao", models.CharField(max_length=255)),
                ("fornecedor", models.CharField(max_length=255)),
                ("valor", models.DecimalField(decimal_places=2, max_digits=12)),
                ("data_vencimento", models.DateField()),
                ("data_pagamento", models.DateField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("aberta", "Aberta"), ("paga", "Paga"), ("atrasada", "Atrasada")],
                        default="aberta",
                        max_length=16,
                    ),
                ),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["data_vencimento", "id"]},
        ),
        migrations.CreateModel(
            name="ContaReceber",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("descricao", models.CharField(max_length=255)),
                ("cliente", models.CharField(max_length=255)),
                ("valor", models.DecimalField(decimal_places=2, max_digits=12)),
                ("data_vencimento", models.DateField()),
                ("data_recebimento", models.DateField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("aberta", "Aberta"), ("recebida", "Recebida"), ("atrasada", "Atrasada")],
                        default="aberta",
                        max_length=16,
                    ),
                ),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["data_vencimento", "id"]},
        ),
        migrations.CreateModel(
            name="FluxoCaixaLancamento",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("data_lancamento", models.DateField()),
                (
                    "tipo",
                    models.CharField(
                        choices=[("entrada", "Entrada"), ("saida", "Saída")],
                        max_length=16,
                    ),
                ),
                ("valor", models.DecimalField(decimal_places=2, max_digits=12)),
                ("categoria", models.CharField(max_length=255)),
                ("referencia", models.CharField(blank=True, max_length=255)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-data_lancamento", "-id"]},
        ),
    ]
