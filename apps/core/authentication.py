"""Autenticação entre serviços por API Key."""

import hmac

from django.conf import settings
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from rest_framework.request import Request


class UsuarioServico:
    """Representa o serviço que chamou a API com uma API Key válida.

    Não existe usuário final: a chave indica apenas que a chamada vem de
    um serviço autorizado.
    """

    is_authenticated = True
    is_active = True
    is_anonymous = False

    def __str__(self) -> str:
        """Retorna um nome legível para logs."""
        return "servico-autenticado"


class AutenticacaoApiKey(BaseAuthentication):
    """Autentica requisições pela API Key enviada em um header HTTP.

    O nome do header vem de ``settings.API_KEY_HEADER`` e o valor
    esperado, de ``settings.API_KEY``.
    """

    def authenticate(
        self, request: Request
    ) -> tuple[UsuarioServico, None] | None:
        """Valida a API Key recebida no header.

        Args:
            request: Requisição HTTP recebida.

        Returns:
            Tupla ``(UsuarioServico, None)`` quando a chave é válida, ou
            None quando o header não foi enviado.

        Raises:
            AuthenticationFailed: Se a chave enviada for inválida ou se
                ``API_KEY`` não estiver configurada no ambiente.
        """
        chave_recebida = request.headers.get(settings.API_KEY_HEADER)
        if chave_recebida is None:
            return None

        chave_esperada = settings.API_KEY
        if not chave_esperada or not hmac.compare_digest(
            chave_recebida.encode(), chave_esperada.encode()
        ):
            raise exceptions.AuthenticationFailed("API Key inválida.")

        return UsuarioServico(), None

    def authenticate_header(self, request: Request) -> str:
        """Informa o header esperado nas respostas 401.

        Args:
            request: Requisição HTTP recebida.

        Returns:
            Nome do header da API Key, enviado em ``WWW-Authenticate``.
        """
        return str(settings.API_KEY_HEADER)
