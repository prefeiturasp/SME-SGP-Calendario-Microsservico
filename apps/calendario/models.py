"""Models do app calendario."""

from django.db import models

from apps.core.models import ModeloBase


class Modalidade(models.Model):
    """Representa uma modalidade de ensino."""

    id = models.BigAutoField(primary_key=True)
    descricao = models.CharField(max_length=200, null=True)
    codigo_uuid = models.UUIDField(null=True, unique=True)

    class Meta:
        """Configura o mapeamento da tabela."""

        db_table = "modalidade"


class TipoCalendario(ModeloBase):
    """Representa um tipo de calendário escolar."""

    id = models.BigAutoField(primary_key=True)
    ano_letivo = models.IntegerField()
    nome = models.CharField(max_length=50)
    situacao = models.BooleanField(default=True, db_default=True)
    migrado = models.BooleanField(default=False, db_default=False)
    semestre = models.IntegerField(null=True)
    modalidade = models.ForeignKey(
        Modalidade,
        db_column="id_modalidade",
        null=True,
        on_delete=models.DO_NOTHING,
    )
    periodo = models.IntegerField(null=True)

    class Meta:
        """Configura o mapeamento da tabela."""

        db_table = "tipo_calendario"
