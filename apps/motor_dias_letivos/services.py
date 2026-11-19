"""Geração e consulta da visão de dias letivos do calendário."""

from typing import Any

from apps.core.auditoria import UsuarioAuditoria
from apps.motor_dias_letivos.dominio.dados_calendario import Escopo


class ServicoVisaoCalendario:
    """Gera, grava e consulta a visão de dias letivos de um calendário."""

    def gerar(
        self,
        tipo_calendario_id: int,
        ue_codigo: str | None = None,
        usuario: UsuarioAuditoria | None = None,
    ) -> dict[str, Any]:
        """Calcula e grava a visão do calendário da SME ou de uma UE.

        Args:
            tipo_calendario_id: Id do tipo de calendário.
            ue_codigo: Código da UE; nulo gera a visão da SME.
            usuario: Quem pediu a geração; sem usuário, vale o sistema.

        Returns:
            Total, mínimo e dias que faltam.

        Raises:
            ErroDominio: ``CALENDARIO_NAO_ENCONTRADO``,
                ``CALENDARIO_SEM_BIMESTRES`` ou ``BIMESTRES_INVALIDOS``.
        """
        raise NotImplementedError

    def consultar(
        self, tipo_calendario_id: int, ue_codigo: str | None = None
    ) -> dict[str, Any]:
        """Retorna a visão gravada, sem recalcular.

        Sem visão própria, a UE recebe a visão da SME.

        Args:
            tipo_calendario_id: Id do tipo de calendário.
            ue_codigo: Código da UE; nulo consulta a visão da SME.

        Returns:
            Totais por mês, bimestre e semestre e os dias.

        Raises:
            ErroDominio: ``VISAO_NAO_GERADA`` se não há visão gravada.
        """
        raise NotImplementedError


def registrar_mudanca_no_calendario(
    antes: Escopo | None, depois: Escopo | None
) -> None:
    """Avisa que um dado do calendário mudou e a visão precisa ser regerada.

    Args:
        antes: Calendário afetado antes da mudança.
        depois: Calendário afetado depois da mudança.

    Raises:
        ValueError: Se os dois escopos forem nulos.
    """
    if antes is None and depois is None:
        raise ValueError("Informe ao menos um escopo.")
