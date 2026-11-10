"""Configuração do app core."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Registra o app core no Django."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Core"
