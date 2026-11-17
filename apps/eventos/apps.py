"""Configuração do app eventos."""

from django.apps import AppConfig


class EventosConfig(AppConfig):
    """Registra o app eventos no Django."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.eventos"
    verbose_name = "Eventos"
