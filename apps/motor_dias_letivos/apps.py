"""Configuração do app motor_dias_letivos."""

from django.apps import AppConfig


class MotorDiasLetivosConfig(AppConfig):
    """Registra o app motor_dias_letivos no Django."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.motor_dias_letivos"
    verbose_name = "Motor de dias letivos"
