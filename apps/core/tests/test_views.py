"""Testes das views do app core e da documentação da API."""

from django.test import SimpleTestCase
from django.urls import reverse
from rest_framework.test import APIClient


class HealthViewTest(SimpleTestCase):
    """Testes do endpoint ``GET /api/v1/health/``."""

    def test_retorna_status_ok_sem_autenticacao(self) -> None:
        """O health é público e responde ``{"status": "ok"}``."""
        resposta = APIClient().get(reverse("health-check"))

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json(), {"status": "ok"})

    def test_rota_e_api_v1_health(self) -> None:
        """A rota do health é ``/api/v1/health/``."""
        self.assertEqual(reverse("health-check"), "/api/v1/health/")


class DocumentacaoApiTest(SimpleTestCase):
    """Testes do schema OpenAPI e da Swagger UI."""

    def test_schema_publico_documenta_api_key(self) -> None:
        """O schema é público e declara o esquema de segurança ApiKey."""
        resposta = APIClient().get(reverse("schema"), {"format": "json"})

        self.assertEqual(resposta.status_code, 200)
        esquemas = resposta.json()["components"]["securitySchemes"]
        self.assertEqual(esquemas["ApiKey"]["type"], "apiKey")

    def test_swagger_publico(self) -> None:
        """A Swagger UI é pública."""
        resposta = APIClient().get(reverse("swagger-ui"))

        self.assertEqual(resposta.status_code, 200)
