"""Models do app calendario."""

from django.db import models
from django.db.models.functions import Now


class Modalidade(models.Model):
    """Representa uma modalidade de ensino."""

    id = models.BigAutoField(primary_key=True)
    descricao = models.CharField(max_length=200, null=True)
    codigo_uuid = models.UUIDField(null=True, unique=True)

    class Meta:
        """Configura o mapeamento da tabela."""

        db_table = "modalidade"


class TipoCalendario(models.Model):
    """Representa um tipo de calendário escolar."""

    id = models.BigAutoField(primary_key=True)
    ano_letivo = models.IntegerField()
    nome = models.CharField(max_length=50)
    situacao = models.BooleanField(default=True, db_default=True)
    criado_em = models.DateTimeField(db_default=Now())
    alterado_em = models.DateTimeField(null=True)
    excluido = models.BooleanField(default=False, db_default=False)
    migrado = models.BooleanField(default=False, db_default=False)
    semestre = models.IntegerField(null=True)
    modalidade = models.ForeignKey(
        Modalidade,
        db_column="id_modalidade",
        null=True,
        on_delete=models.DO_NOTHING,
    )
    periodo = models.IntegerField(null=True)
    criado_rf = models.CharField(max_length=100, null=True)
    alterado_rf = models.CharField(max_length=100, null=True)
    criado_por = models.CharField(max_length=200, null=True)
    alterado_por = models.CharField(max_length=200, null=True)
    codigo_uuid = models.UUIDField(null=True, unique=True)

    class Meta:
        """Configura o mapeamento da tabela."""

        db_table = "tipo_calendario"
