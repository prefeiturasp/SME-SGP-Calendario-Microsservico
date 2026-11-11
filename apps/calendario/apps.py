"""Configuração do app calendario."""

from django.apps import AppConfig


class CalendarioConfig(AppConfig):
    """Registra o app calendario no Django."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.calendario"
    verbose_name = "Calendário"
