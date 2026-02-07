from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Produto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=255)),
                ("sku", models.CharField(max_length=64, unique=True)),
                ("unidade", models.CharField(default="UN", max_length=16)),
                ("ativo", models.BooleanField(default=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="MovimentacaoEstoque",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("data_movimentacao", models.DateField()),
                (
                    "tipo",
                    models.CharField(
                        choices=[("entrada", "Entrada"), ("saida", "Saída"), ("ajuste", "Ajuste")],
                        max_length=16,
                    ),
                ),
                ("quantidade", models.DecimalField(decimal_places=2, max_digits=12)),
                ("custo_unitario", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("origem", models.CharField(blank=True, max_length=255)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                (
                    "produto",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="movimentacoes", to="estoque.produto"),
                ),
            ],
            options={"ordering": ["-data_movimentacao", "-id"]},
        ),
    ]
