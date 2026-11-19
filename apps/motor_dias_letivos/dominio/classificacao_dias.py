"""Classificação de cada data do calendário em letiva ou não letiva."""

from enum import Enum

from apps.core.constants import EventoLetivo, TipoEvento
from apps.motor_dias_letivos.dominio.dados_calendario import Calendario, Evento
from apps.motor_dias_letivos.dominio.resultados import ResultadoCalendario


class Efeito(Enum):
    """Efeito de um evento sobre os dias que ele cobre."""

    TORNA_LETIVO = "TORNA_LETIVO"
    TIRA_O_DIA = "TIRA_O_DIA"
    NAO_ALTERA = "NAO_ALTERA"


def efeito_do_evento(evento: Evento) -> Efeito:
    """Retorna o efeito do evento na contagem de dias letivos.

    Args:
        evento: Evento aprovado do calendário.

    Returns:
        Efeito do evento nos dias que ele cobre.
    """
    if not evento.eh_da_sme and not evento.eh_da_ue:
        return Efeito.NAO_ALTERA
    if evento.tipo_codigo in (
        TipoEvento.REUNIAO_PEDAGOGICA,
        TipoEvento.CONSELHO_DE_CLASSE,
    ):
        return Efeito.TIRA_O_DIA
    if evento.tipo_codigo in (
        TipoEvento.RECREIO_NAS_FERIAS,
        TipoEvento.FECHAMENTO_BIMESTRE,
        TipoEvento.SONDAGEM,
        TipoEvento.LIBERACAO_EXCEPCIONAL,
    ):
        return Efeito.NAO_ALTERA
    if evento.letivo == EventoLetivo.SIM:
        if evento.tipo_codigo == TipoEvento.REPOSICAO_DE_AULA:
            return Efeito.NAO_ALTERA
        return Efeito.TORNA_LETIVO
    if evento.letivo == EventoLetivo.NAO:
        return Efeito.TIRA_O_DIA
    return Efeito.NAO_ALTERA


def classificar_calendario(calendario: Calendario) -> ResultadoCalendario:
    """Classifica todas as datas do calendário e soma os dias letivos.

    Usa os eventos da SME e, quando o calendário tem UE, também os dela.

    Args:
        calendario: Calendário montado com bimestres, eventos e feriados.

    Returns:
        Uma decisão por data, em ordem, com os totais por mês, bimestre,
        semestre e ano.
    """
    raise NotImplementedError
