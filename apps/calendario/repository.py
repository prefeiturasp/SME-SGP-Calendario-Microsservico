"""Acesso ao banco do app calendario.

Única camada que executa queries ORM. Retorna dict ou tipos
primitivos, nunca instâncias de model.
"""

from typing import cast

from django.db import models

from apps.calendario.models import Modalidade, TipoCalendario
from apps.core.repository import RepositorioBase, RespostaPaginada


class RepositorioTipoCalendario(RepositorioBase[TipoCalendario]):
    """Persiste tipos de calendário com as operações compartilhadas."""

    def __init__(self) -> None:
        """Configura o model de tipo de calendário."""
        super().__init__(TipoCalendario)


class RepositorioModalidade:
    """Consulta modalidades de ensino."""

    def __init__(self) -> None:
        """Configura o gerenciador de modalidades."""
        self.gerenciador = cast(
            models.Manager[Modalidade],
            Modalidade._default_manager,
        )

    def listar(
        self,
        pagina_atual: int,
        tamanho_pagina: int,
    ) -> RespostaPaginada:
        """Lista uma página de modalidades ordenadas pelo identificador.

        Args:
            pagina_atual: Número da página, iniciado em zero.
            tamanho_pagina: Quantidade máxima de itens da página.

        Returns:
            Itens da página e metadados da paginação.

        Raises:
            ValueError: Quando os parâmetros são negativos.
        """
        if pagina_atual < 0 or tamanho_pagina < 0:
            raise ValueError(
                "Os parâmetros de paginação não podem ser negativos."
            )

        registros = self.gerenciador.order_by(Modalidade._meta.pk.name)
        total_itens = registros.count()
        inicio = pagina_atual * tamanho_pagina
        fim = inicio + tamanho_pagina
        itens = [dict(registro) for registro in registros.values()[inicio:fim]]
        return {
            "itens": itens,
            "tamanho_pagina": tamanho_pagina,
            "total_itens": total_itens,
            "pagina_atual": pagina_atual,
        }
