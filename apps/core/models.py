"""Models compartilhados entre os apps."""

from django.db import models
from django.utils import timezone

from apps.core.auditoria import SISTEMA, UsuarioAuditoria


class ModeloBase(models.Model):
    """Base das tabelas com as colunas de auditoria do SGP."""

    criado_em = models.DateTimeField()
    criado_por = models.CharField(max_length=200)
    criado_rf = models.CharField(max_length=200)
    alterado_em = models.DateTimeField(null=True, blank=True)
    alterado_por = models.CharField(max_length=200, null=True, blank=True)
    alterado_rf = models.CharField(max_length=200, null=True, blank=True)
    excluido = models.BooleanField(default=False)
    codigo_uuid = models.UUIDField(null=True, blank=True, unique=True)

    class Meta:
        """Não cria tabela para a base."""

        abstract = True

    def marcar_criacao(self, usuario: UsuarioAuditoria = SISTEMA) -> None:
        """Preenche data e autor da criação, sem gravar no banco.

        Args:
            usuario: Quem criou o registro; sem usuário, vale o sistema.
        """
        self.criado_em = timezone.now()
        self.criado_por = usuario.nome
        self.criado_rf = usuario.rf

    def marcar_alteracao(self, usuario: UsuarioAuditoria = SISTEMA) -> None:
        """Preenche data e autor da alteração, sem gravar no banco.

        Args:
            usuario: Quem alterou o registro; sem usuário, vale o sistema.
        """
        self.alterado_em = timezone.now()
        self.alterado_por = usuario.nome
        self.alterado_rf = usuario.rf
