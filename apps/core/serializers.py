"""Serializers do app core."""

from rest_framework import serializers


class HealthSerializer(serializers.Serializer):
    """Formato da resposta do endpoint de health."""

    status = serializers.CharField(help_text="Situação do serviço.")
