"""Regras de negócio do app calendario.

Orquestra os repositórios. Não importa do DRF nem do HTTP do Django.
"""

from collections.abc import Mapping, Sequence

from apps.core.auditoria import SISTEMA, UsuarioAuditoria
from apps.core.repository import RespostaPaginada


class ServicoTipoCalendario:
    """Define os casos de uso de tipos de calendário."""

    def listar(
        self,
        pagina_atual: int,
        tamanho_pagina: int,
        filtros: Mapping[str, object],
    ) -> RespostaPaginada | None:
        """Lista uma página de tipos de calendário.

        Args:
            pagina_atual: Número da página, iniciado em zero.
            tamanho_pagina: Quantidade máxima de itens da página.
            filtros: Critérios aplicados à listagem.
        """
        pass

    def inserir(
        self,
        dados: Mapping[str, object],
        usuario: UsuarioAuditoria = SISTEMA,
    ) -> dict[str, object] | None:
        """Insere um tipo de calendário."""
        pass

    def obter_por_id(
        self,
        identificador: object,
    ) -> dict[str, object] | None:
        """Obtém um tipo de calendário pelo identificador."""
        pass

    def atualizar(
        self,
        identificador: object,
        dados: Mapping[str, object],
        usuario: UsuarioAuditoria = SISTEMA,
    ) -> dict[str, object] | None:
        """Atualiza um tipo de calendário."""
        pass

    def excluir(
        self,
        identificadores: Sequence[object],
        usuario: UsuarioAuditoria = SISTEMA,
    ) -> int | None:
        """Exclui tipos de calendário."""
        pass


class ServicoModalidade:
    """Define os casos de uso de modalidades de ensino."""

    def listar(
        self,
        pagina_atual: int,
        tamanho_pagina: int,
        filtros: Mapping[str, object],
    ) -> RespostaPaginada | None:
        """Lista uma página de modalidades de ensino.

        Args:
            pagina_atual: Número da página, iniciado em zero.
            tamanho_pagina: Quantidade máxima de itens da página.
            filtros: Critérios aplicados à listagem.
        """
        pass
