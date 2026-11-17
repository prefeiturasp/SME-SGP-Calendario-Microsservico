"""Testes dos valores compartilhados de auditoria."""

from dataclasses import FrozenInstanceError

from django.test import SimpleTestCase

from apps.core.auditoria import SISTEMA, UsuarioAuditoria


class TestUsuarioAuditoria(SimpleTestCase):
    """Valida a identificação usada nas colunas de auditoria."""

    def test_sistema_tem_identificacao_padrao(self) -> None:
        """Mantém nome e RF convencionados para operações do sistema."""
        self.assertEqual(SISTEMA, UsuarioAuditoria(nome="Sistema", rf="0"))

    def test_usuario_e_imutavel(self) -> None:
        """Impede alteração da autoria depois de sua criação."""
        usuario = UsuarioAuditoria(nome="Maria", rf="1234567")
        atributo = "nome"

        with self.assertRaises(FrozenInstanceError):
            setattr(usuario, atributo, "Outro nome")
