"""Leitura de um calendário completo do banco."""

from apps.motor_dias_letivos.dominio.dados_calendario import Calendario


def montar_calendario(
    tipo_calendario_id: int, ue_codigo: str | None = None
) -> Calendario:
    """Monta o calendário com bimestres, eventos e feriados fixos.

    Traz só eventos aprovados e de tipo ativo: os da SME e,
    quando ``ue_codigo`` é informado, também os da UE.

    Args:
        tipo_calendario_id: Id do tipo de calendário.
        ue_codigo: Código da UE; nulo monta o calendário da SME.

    Returns:
        Calendário pronto para o motor.

    Raises:
        ErroDominio: ``CALENDARIO_NAO_ENCONTRADO`` se o tipo não existe ou
            foi excluído.
    """
    raise NotImplementedError
