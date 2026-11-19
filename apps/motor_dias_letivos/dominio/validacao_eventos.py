"""Validação de evento antes de gravar."""

from apps.motor_dias_letivos.dominio.dados_calendario import (
    Calendario,
    Evento,
)
from apps.motor_dias_letivos.dominio.resultados import Violacao


def letivo_coerente_com_tipo(
    letivo_do_tipo: int, letivo_do_evento: int
) -> bool:
    """Verifica se o letivo do evento combina com o do tipo de evento.

    Args:
        letivo_do_tipo: Valor de ``letivo`` do tipo de evento.
        letivo_do_evento: Valor de ``letivo`` escolhido no evento.

    Returns:
        True quando a combinação é aceita.
    """
    raise NotImplementedError


def validar_evento(
    evento: Evento,
    calendario: Calendario,
    data_confirmada: bool = False,
) -> list[Violacao]:
    """Valida um evento contra as regras do calendário.

    Args:
        evento: Evento que está sendo incluído ou alterado.
        calendario: Calendário do evento, montado com a UE do evento.
        data_confirmada: Se o usuário já confirmou manter uma Liberação
            Excepcional fora do período escolar.

    Returns:
        Violações encontradas, uma por código; vazia quando o evento é
        válido.
    """
    raise NotImplementedError


def exige_aprovacao(evento: Evento, calendario: Calendario) -> bool:
    """Verifica se o evento precisa de aprovação antes de valer.

    Args:
        evento: Evento já validado.
        calendario: Calendário do evento, montado com a UE do evento.

    Returns:
        True quando o evento só foi aceito por Liberação Excepcional.
    """
    raise NotImplementedError
