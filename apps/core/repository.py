"""Operações de persistência compartilhadas entre os apps."""

from collections.abc import Mapping, Sequence
from typing import Generic, TypedDict, TypeVar, cast

from django.db import models
from django.utils import timezone

from apps.core.auditoria import SISTEMA, UsuarioAuditoria
from apps.core.models import ModeloBase

ModeloT = TypeVar("ModeloT", bound=ModeloBase)


class RespostaPaginada(TypedDict):
    """Representa registros e metadados de uma página."""

    itens: list[dict[str, object]]
    tamanho_pagina: int
    total_itens: int
    pagina_atual: int


class RepositorioBase(Generic[ModeloT]):
    """Oferece persistência comum para models baseados em ``ModeloBase``."""

    def __init__(self, modelo: type[ModeloT]) -> None:
        """Configura o model manipulado pelo repositório.

        Args:
            modelo: Classe concreta do model persistido.
        """
        self.modelo = modelo
        self.gerenciador = cast(
            models.Manager[ModeloT],
            modelo._default_manager,
        )

    def listar(
        self,
        pagina_atual: int,
        tamanho_pagina: int,
    ) -> RespostaPaginada:
        """Lista uma página dos registros ativos.

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

        registros = self.gerenciador.filter(excluido=False).order_by(
            self.modelo._meta.pk.name
        )
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

    def inserir(
        self,
        dados: Mapping[str, object],
        usuario: UsuarioAuditoria = SISTEMA,
    ) -> dict[str, object]:
        """Insere um registro com a autoria da criação.

        Args:
            dados: Valores dos campos do novo registro.
            usuario: Responsável pela criação.

        Returns:
            Registro persistido no formato de dicionário.
        """
        instancia = self.modelo(**dados)
        instancia.marcar_criacao(usuario)
        instancia.save()
        return self._obter_dados(instancia.pk)

    def atualizar(
        self,
        identificador: object,
        dados: Mapping[str, object],
        usuario: UsuarioAuditoria = SISTEMA,
    ) -> dict[str, object]:
        """Atualiza um registro ativo e grava a autoria da alteração.

        Args:
            identificador: Chave primária do registro.
            dados: Novos valores dos campos.
            usuario: Responsável pela alteração.

        Returns:
            Registro atualizado no formato de dicionário.

        Raises:
            ObjectDoesNotExist: Quando o registro não existe ou está
                excluído logicamente.
        """
        instancia = self.gerenciador.get(
            pk=identificador,
            excluido=False,
        )
        for campo, valor in dados.items():
            setattr(instancia, campo, valor)
        instancia.marcar_alteracao(usuario)
        instancia.save()
        return self._obter_dados(instancia.pk)

    def excluir(
        self,
        identificadores: Sequence[object],
        usuario: UsuarioAuditoria = SISTEMA,
    ) -> int:
        """Exclui logicamente uma lista de registros ativos.

        Args:
            identificadores: Chaves primárias dos registros.
            usuario: Responsável pela exclusão.

        Returns:
            Quantidade de registros excluídos.
        """
        quantidade = self.gerenciador.filter(
            pk__in=identificadores,
            excluido=False,
        ).update(
            excluido=True,
            alterado_em=timezone.now(),
            alterado_por=usuario.nome,
            alterado_rf=usuario.rf,
        )
        return quantidade

    def _obter_dados(self, identificador: object) -> dict[str, object]:
        """Obtém todos os campos persistidos de um registro."""
        registro = self.gerenciador.values().get(pk=identificador)
        return cast(dict[str, object], registro)
