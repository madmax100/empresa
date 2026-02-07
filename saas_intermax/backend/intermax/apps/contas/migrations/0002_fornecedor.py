from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("contas", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Fornecedor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=255)),
                ("tipo", models.CharField(blank=True, max_length=64)),
                ("especificacao", models.CharField(blank=True, max_length=128)),
            ],
        ),
        migrations.AlterField(
            model_name="contapagar",
            name="fornecedor",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="contas.fornecedor"),
        ),
    ]
