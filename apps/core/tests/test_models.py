"""Testes dos models compartilhados do app core."""

from datetime import UTC, datetime
from typing import cast
from unittest.mock import patch

from django.db import models
from django.db.models.functions import Now
from django.test import SimpleTestCase

from apps.core.auditoria import UsuarioAuditoria
from apps.core.models import ModeloBase


class ModeloConcretoTeste(ModeloBase):
    """Implementa a base sem criar uma tabela para estes testes."""

    class Meta:
        """Mantém o model concreto fora do gerenciamento do Django."""

        app_label = "core"
        managed = False


class TestModeloBase(SimpleTestCase):
    """Valida o contrato abstrato das colunas de auditoria."""

    def test_modelo_e_abstrato(self) -> None:
        """Não cria tabela própria para a classe compartilhada."""
        self.assertTrue(ModeloBase._meta.abstract)

    def test_campos_de_auditoria(self) -> None:
        """Expõe campos obrigatórios e opcionais de auditoria."""
        criado_em = cast(
            "models.Field[object, object]",
            ModeloBase._meta.get_field("criado_em"),
        )
        self.assertFalse(criado_em.null)
        self.assertIsInstance(criado_em.db_default, Now)

        limites = {
            "criado_por": 200,
            "criado_rf": 100,
            "alterado_por": 200,
            "alterado_rf": 100,
        }
        for nome, limite in limites.items():
            campo = cast(
                "models.Field[object, object]",
                ModeloBase._meta.get_field(nome),
            )
            self.assertTrue(campo.null)
            self.assertEqual(campo.max_length, limite)

        alterado_em = cast(
            "models.Field[object, object]",
            ModeloBase._meta.get_field("alterado_em"),
        )
        self.assertTrue(alterado_em.null)

        campo_excluido = cast(
            "models.Field[object, object]",
            ModeloBase._meta.get_field("excluido"),
        )
        self.assertFalse(campo_excluido.default)
        self.assertFalse(campo_excluido.db_default)

    def test_codigo_uuid_e_opcional_e_unico(self) -> None:
        """Representa o UUID opcional protegido por unicidade."""
        campo = cast(
            "models.Field[object, object]",
            ModeloBase._meta.get_field("codigo_uuid"),
        )

        self.assertTrue(campo.null)
        self.assertTrue(campo.unique)

    def test_marca_criacao_com_usuario_informado(self) -> None:
        """Preenche a criação com data, nome e RF recebidos."""
        instante = datetime(2026, 11, 17, 10, 30, tzinfo=UTC)
        usuario = UsuarioAuditoria(nome="Maria", rf="1234567")
        modelo = ModeloConcretoTeste()

        with patch("apps.core.models.timezone.now", return_value=instante):
            modelo.marcar_criacao(usuario)

        self.assertEqual(modelo.criado_em, instante)
        self.assertEqual(modelo.criado_por, "Maria")
        self.assertEqual(modelo.criado_rf, "1234567")

    def test_marca_alteracao_com_usuario_sistema(self) -> None:
        """Usa a identificação do sistema quando o usuário é omitido."""
        instante = datetime(2026, 11, 17, 11, 30, tzinfo=UTC)
        modelo = ModeloConcretoTeste()

        with patch("apps.core.models.timezone.now", return_value=instante):
            modelo.marcar_alteracao()

        self.assertEqual(modelo.alterado_em, instante)
        self.assertEqual(modelo.alterado_por, "Sistema")
        self.assertEqual(modelo.alterado_rf, "0")
