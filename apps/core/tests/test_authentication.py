"""Testes da autenticação por API Key."""

from django.test import SimpleTestCase, override_settings
from django.urls import path, reverse
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.test import APIClient
from rest_framework.views import APIView

from apps.core.authentication import UsuarioServico


class ViewProtegida(APIView):
    """View de teste que usa a autenticação padrão do projeto."""

    def get(self, request: Request) -> Response:
        """Retorna 200 quando a autenticação passa.

        Args:
            request: Requisição HTTP recebida.

        Returns:
            Resposta 200 com ``{"ok": True}``.
        """
        return Response({"ok": True})


urlpatterns = [
    path("protegida/", ViewProtegida.as_view(), name="protegida"),
]


@override_settings(
    ROOT_URLCONF=__name__,
    API_KEY="chave-de-teste",
    API_KEY_HEADER="X-API-Key",
)
class AutenticacaoApiKeyTest(SimpleTestCase):
    """Garante que endpoints protegidos exigem a API Key."""

    def setUp(self) -> None:
        """Cria o cliente HTTP e a URL da view protegida."""
        self.cliente = APIClient()
        self.url = reverse("protegida")

    def test_sem_api_key_retorna_401(self) -> None:
        """Sem o header, a resposta é 401 e indica o header esperado."""
        resposta = self.cliente.get(self.url)

        self.assertEqual(resposta.status_code, 401)
        self.assertEqual(resposta["WWW-Authenticate"], "X-API-Key")

    def test_api_key_invalida_retorna_401(self) -> None:
        """Com uma chave diferente da configurada, a resposta é 401."""
        resposta = self.cliente.get(self.url, HTTP_X_API_KEY="errada")

        self.assertEqual(resposta.status_code, 401)

    def test_api_key_valida_retorna_200(self) -> None:
        """Com a chave configurada, a view protegida responde 200."""
        resposta = self.cliente.get(self.url, HTTP_X_API_KEY="chave-de-teste")

        self.assertEqual(resposta.status_code, 200)

    @override_settings(API_KEY="")
    def test_api_key_nao_configurada_recusa_tudo(self) -> None:
        """Sem API_KEY no ambiente, nem uma chave vazia é aceita."""
        resposta = self.cliente.get(self.url, HTTP_X_API_KEY="")

        self.assertEqual(resposta.status_code, 401)

    def test_usuario_servico_tem_nome_legivel(self) -> None:
        """O usuário autenticado aparece com nome legível nos logs."""
        self.assertEqual(str(UsuarioServico()), "servico-autenticado")
