from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("estoque", "0002_expand_estoque"),
        ("faturamento", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="NotaFiscal",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("numero_nota", models.CharField(max_length=64)),
                ("data_emissao", models.DateField()),
                (
                    "tipo",
                    models.CharField(
                        choices=[("entrada", "Entrada"), ("saida", "Saída"), ("servico", "Serviço")],
                        max_length=16,
                    ),
                ),
                ("operacao", models.CharField(max_length=64)),
                ("fornecedor", models.CharField(blank=True, max_length=255)),
                ("cliente", models.CharField(blank=True, max_length=255)),
                ("valor_produtos", models.DecimalField(decimal_places=2, max_digits=12)),
                ("valor_total", models.DecimalField(decimal_places=2, max_digits=12)),
                ("impostos", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
            ],
            options={"ordering": ["-data_emissao", "-id"]},
        ),
        migrations.CreateModel(
            name="ItemNotaFiscal",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantidade", models.DecimalField(decimal_places=2, max_digits=12)),
                ("valor_unitario", models.DecimalField(decimal_places=2, max_digits=12)),
                (
                    "nota",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="itens", to="faturamento.notafiscal"),
                ),
                (
                    "produto",
                    models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="estoque.produto"),
                ),
            ],
        ),
    ]
