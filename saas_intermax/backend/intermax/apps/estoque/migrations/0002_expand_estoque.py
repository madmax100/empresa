from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("estoque", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="produto",
            name="categoria",
            field=models.CharField(default="OUTROS", max_length=64),
        ),
        migrations.AddField(
            model_name="produto",
            name="estoque_minimo",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name="produto",
            name="disponivel_locacao",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="produto",
            name="preco_entrada",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name="movimentacaoestoque",
            name="valor_unitario",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name="movimentacaoestoque",
            name="observacoes",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="movimentacaoestoque",
            name="documento_referencia",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.CreateModel(
            name="LocalEstoque",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=128)),
                ("descricao", models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="TipoMovimentacaoEstoque",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("codigo", models.CharField(max_length=8, unique=True)),
                ("descricao", models.CharField(max_length=128)),
                (
                    "tipo",
                    models.CharField(choices=[("E", "Entrada"), ("S", "Saída")], max_length=1),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SaldoEstoque",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantidade", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("quantidade_reservada", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("custo_medio", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("ultima_movimentacao", models.DateField(blank=True, null=True)),
                (
                    "local",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="saldos", to="estoque.localestoque"),
                ),
                (
                    "produto",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="saldos", to="estoque.produto"),
                ),
            ],
            options={"ordering": ["produto_id"]},
        ),
        migrations.CreateModel(
            name="PosicaoEstoque",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("codigo", models.CharField(max_length=64)),
                ("descricao", models.CharField(blank=True, max_length=255)),
                (
                    "local",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="posicoes", to="estoque.localestoque"),
                ),
            ],
        ),
    ]
