"""Classificação de cada data do calendário em letiva ou não letiva."""

from apps.motor_dias_letivos.dominio.dados_calendario import Calendario
from apps.motor_dias_letivos.dominio.resultados import ResultadoCalendario


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
