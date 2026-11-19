"""Feriados fixos, móveis e do calendário."""

from collections.abc import Iterable
from datetime import date, timedelta

from apps.core.constants import TipoEvento
from apps.motor_dias_letivos.dominio.dados_calendario import (
    Evento,
    FeriadoFixo,
)

# Distância, em dias, de cada feriado móvel até a Páscoa.
_FERIADOS_MOVEIS = (
    (-2, "Sexta-feira Santa"),
    (0, "Páscoa"),
    (60, "Corpus Christi"),
)


def _pascoa(ano: int) -> date:
    # Mesmo cálculo do legado (ServicoFeriadoCalendario.cs:54-75)
    r1 = ano % 19
    r2 = ano % 4
    r3 = ano % 7
    r4 = (19 * r1 + 24) % 30
    r5 = (6 * r4 + 4 * r3 + 2 * r2 + 5) % 7
    pascoa = date(ano, 3, 22) + timedelta(days=r4 + r5)
    if pascoa == date(ano, 4, 26):
        return date(ano, 4, 19)
    if pascoa == date(ano, 4, 25) and r1 > 10:
        return date(ano, 4, 18)
    return pascoa


def feriados_moveis(ano: int) -> list[tuple[date, str]]:
    """Lista os feriados móveis do ano.

    Inclui Sexta-feira Santa, Páscoa e Corpus Christi. O Carnaval depende
    do evento cadastrado pela COPED/SME.

    Args:
        ano: Ano dos feriados.

    Returns:
        Pares ``(data, nome)`` em ordem de data.
    """
    pascoa = _pascoa(ano)
    return [
        (pascoa + timedelta(days=distancia), nome)
        for distancia, nome in _FERIADOS_MOVEIS
    ]


def _feriado_fixo_no_ano(ano: int, feriado: FeriadoFixo) -> date | None:
    try:
        return date(ano, feriado.mes, feriado.dia)
    except ValueError:
        return None


def feriados_do_ano(
    ano: int,
    eventos: Iterable[Evento],
    fixos: Iterable[FeriadoFixo],
) -> set[date]:
    """Retorna todos os feriados de um ano.

    Junta os dias dos eventos de Feriado da SME, feriados fixos e os móveis.

    Args:
        ano: Ano dos feriados.
        eventos: Eventos do calendário; só os de Feriado da SME contam.
        fixos: Feriados fixos.

    Returns:
        Datas de feriado do ano.
    """
    dos_eventos = {
        dia
        for evento in eventos
        if evento.tipo_codigo == TipoEvento.FERIADO and evento.eh_da_sme
        for dia in evento.dias()
        if dia.year == ano
    }
    do_catalogo = {
        data
        for feriado in fixos
        if (data := _feriado_fixo_no_ano(ano, feriado)) is not None
    }
    moveis = {data for data, _nome in feriados_moveis(ano)}
    return dos_eventos | do_catalogo | moveis
