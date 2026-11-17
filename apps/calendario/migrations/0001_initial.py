"""Cria o estado inicial do domínio de calendário."""

import django.db.models.functions.datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    """Cria a tabela de tipos de calendário."""

    initial = True

    dependencies: list[tuple[str, str]] = []

    operations = [
        migrations.CreateModel(
            name="Modalidade",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "descricao",
                    models.CharField(max_length=200, null=True),
                ),
                ("codigo_uuid", models.UUIDField(null=True, unique=True)),
            ],
            options={"db_table": "modalidade"},
        ),
        migrations.CreateModel(
            name="TipoCalendario",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("ano_letivo", models.IntegerField()),
                ("nome", models.CharField(max_length=50)),
                (
                    "situacao",
                    models.BooleanField(db_default=True, default=True),
                ),
                (
                    "criado_em",
                    models.DateTimeField(
                        db_default=django.db.models.functions.datetime.Now()
                    ),
                ),
                ("alterado_em", models.DateTimeField(null=True)),
                (
                    "excluido",
                    models.BooleanField(db_default=False, default=False),
                ),
                (
                    "migrado",
                    models.BooleanField(db_default=False, default=False),
                ),
                ("semestre", models.IntegerField(null=True)),
                ("periodo", models.IntegerField(null=True)),
                (
                    "criado_rf",
                    models.CharField(max_length=100, null=True),
                ),
                (
                    "alterado_rf",
                    models.CharField(max_length=100, null=True),
                ),
                (
                    "criado_por",
                    models.CharField(max_length=200, null=True),
                ),
                (
                    "alterado_por",
                    models.CharField(max_length=200, null=True),
                ),
                ("codigo_uuid", models.UUIDField(null=True, unique=True)),
                (
                    "modalidade",
                    models.ForeignKey(
                        db_column="id_modalidade",
                        null=True,
                        on_delete=models.DO_NOTHING,
                        to="calendario.modalidade",
                    ),
                ),
            ],
            options={"db_table": "tipo_calendario"},
        ),
    ]
