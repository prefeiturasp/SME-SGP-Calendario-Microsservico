"""Feriados fixos, móveis e do calendário."""

from collections.abc import Iterable
from datetime import date

from apps.motor_dias_letivos.dominio.dados_calendario import (
    Evento,
    FeriadoFixo,
)


def feriados_moveis(ano: int) -> list[tuple[date, str]]:
    """Lista os feriados móveis do ano.

    Args:
        ano: Ano dos feriados.

    Returns:
        Pares ``(data, nome)`` em ordem de data.
    """
    raise NotImplementedError


def feriados_do_ano(
    ano: int,
    eventos: Iterable[Evento],
    fixos: Iterable[FeriadoFixo],
) -> set[date]:
    """Retorna todos os feriados de um ano.

    Junta os eventos de Feriado da SME, os feriados fixos e os móveis.

    Args:
        ano: Ano dos feriados.
        eventos: Eventos do calendário; só os de Feriado da SME contam.
        fixos: Feriados fixos do catálogo.

    Returns:
        Datas de feriado do ano.
    """
    raise NotImplementedError
