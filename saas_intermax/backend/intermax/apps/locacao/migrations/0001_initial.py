from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ContratoLocacao",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("cliente", models.CharField(max_length=255)),
                ("inicio", models.DateField()),
                ("fim", models.DateField(blank=True, null=True)),
                ("valorcontrato", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("valorpacela", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("numeroparcelas", models.CharField(blank=True, max_length=16)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-inicio", "id"]},
        ),
        migrations.CreateModel(
            name="ItemContratoLocacao",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("descricao", models.CharField(max_length=255)),
                ("quantidade", models.PositiveIntegerField(default=1)),
                ("valor_unitario", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                (
                    "contrato",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="itens", to="locacao.contratolocacao"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SuprimentoNota",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("data", models.DateField()),
                ("valor", models.DecimalField(decimal_places=2, max_digits=12)),
                ("descricao", models.CharField(blank=True, max_length=255)),
                (
                    "contrato",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="suprimentos", to="locacao.contratolocacao"),
                ),
            ],
            options={"ordering": ["-data", "id"]},
        ),
    ]
