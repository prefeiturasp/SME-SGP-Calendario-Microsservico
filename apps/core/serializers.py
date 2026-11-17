"""Serializers do app core."""

from rest_framework import serializers


class RespostaPaginadaSerializer(serializers.Serializer):
    """Formato genérico de uma resposta paginada."""

    itens = serializers.ListField(
        help_text="Itens correspondentes à página atual."
    )
    tamanho_pagina = serializers.IntegerField(
        min_value=0,
        help_text="Quantidade máxima de itens da página.",
    )
    total_itens = serializers.IntegerField(
        min_value=0,
        help_text="Quantidade total de itens encontrados.",
    )
    pagina_atual = serializers.IntegerField(
        min_value=0,
        help_text="Número da página atual.",
    )


class HealthSerializer(serializers.Serializer):
    """Formato da resposta do endpoint de health."""

    status = serializers.CharField(help_text="Situação do serviço.")
