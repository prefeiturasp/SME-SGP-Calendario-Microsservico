"""Rotas do app core, sem prefixo global (vem de config/urls.py)."""

from django.urls import path

from apps.core.api.views import HealthView

urlpatterns = [
    path("health/", HealthView.as_view(), name="health-check"),
]
