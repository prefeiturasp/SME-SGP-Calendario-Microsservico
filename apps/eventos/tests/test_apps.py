"""Testes da configuração do app eventos."""

from django.apps import apps
from django.test import SimpleTestCase

from apps.eventos.apps import EventosConfig


class TestEventosConfig(SimpleTestCase):
    """Valida o registro do app eventos no Django."""

    def test_app_eventos_esta_registrado(self) -> None:
        """Confirma que o Django carrega a configuração de eventos."""
        config = apps.get_app_config("eventos")

        self.assertIsInstance(config, EventosConfig)
        self.assertEqual(config.name, "apps.eventos")
