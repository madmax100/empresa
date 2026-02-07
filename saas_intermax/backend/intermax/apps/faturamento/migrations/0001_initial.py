from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ContratoSuprimento",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("cliente", models.CharField(max_length=255)),
                ("data_inicio", models.DateField()),
                ("data_fim", models.DateField()),
                ("valor_mensal", models.DecimalField(decimal_places=2, max_digits=12)),
                (
                    "status",
                    models.CharField(
                        choices=[("ativo", "Ativo"), ("expirando", "Expirando"), ("pendente", "Pendente")],
                        default="ativo",
                        max_length=16,
                    ),
                ),
                ("observacoes", models.TextField(blank=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["data_fim", "id"]},
        ),
        migrations.CreateModel(
            name="CustoFixo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("descricao", models.CharField(max_length=255)),
                ("centro_custo", models.CharField(max_length=255)),
                ("valor_mensal", models.DecimalField(decimal_places=2, max_digits=12)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["descricao", "id"]},
        ),
        migrations.CreateModel(
            name="CustoVariavel",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("descricao", models.CharField(max_length=255)),
                ("valor", models.DecimalField(decimal_places=2, max_digits=12)),
                ("data_referencia", models.DateField()),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-data_referencia", "-id"]},
        ),
        migrations.CreateModel(
            name="FaturamentoRegistro",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("periodo_inicio", models.DateField()),
                ("periodo_fim", models.DateField()),
                ("receita_bruta", models.DecimalField(decimal_places=2, max_digits=12)),
                ("receita_liquida", models.DecimalField(decimal_places=2, max_digits=12)),
                ("ticket_medio", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-periodo_inicio", "-id"]},
        ),
    ]
