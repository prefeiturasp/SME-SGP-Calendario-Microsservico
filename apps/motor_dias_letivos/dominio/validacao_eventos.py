"""Validação de evento antes de gravar."""

from collections.abc import Callable, Iterable
from datetime import date

from apps.core.constants import EventoLetivo, TipoEvento
from apps.motor_dias_letivos.constants import (
    MENSAGENS_VIOLACAO,
    TIPOS_ISENTOS_VALIDACAO_DATA,
    TIPOS_PERMITIDOS_FORA_DO_BIMESTRE,
    CodigoViolacao,
)
from apps.motor_dias_letivos.dominio.classificacao_dias import (
    Efeito,
    efeito_do_evento,
)
from apps.motor_dias_letivos.dominio.dados_calendario import (
    Calendario,
    Evento,
)
from apps.motor_dias_letivos.dominio.feriados import feriados_do_ano
from apps.motor_dias_letivos.dominio.resultados import Violacao

_DOMINGO = 6


def _violacao(
    codigo: CodigoViolacao, datas: Iterable[date] = ()
) -> list[Violacao]:
    """Cria a violação do código com a mensagem padrão.

    Args:
        codigo: Código da violação.
        datas: Dias recusados; vazio quando a violação não é de data.

    Returns:
        Lista com uma única violação.
    """
    datas = tuple(datas)
    return [Violacao(codigo, MENSAGENS_VIOLACAO[codigo], datas)]


def _violacao_se_houver_datas(
    codigo: CodigoViolacao, datas: list[date]
) -> list[Violacao]:
    """Cria a violação só quando há dias recusados.

    Args:
        codigo: Código da violação.
        datas: Dias recusados.

    Returns:
        Lista com uma violação, ou vazia quando não há dias.
    """
    return _violacao(codigo, datas) if datas else []


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
    if letivo_do_tipo in (EventoLetivo.SIM, EventoLetivo.NAO):
        return letivo_do_evento == letivo_do_tipo
    return True


def exige_datas_em_bimestres(evento: Evento) -> bool:
    """Verifica se todos os dias do evento precisam estar em bimestre.

    Args:
        evento: Evento que está sendo validado.

    Returns:
        True quando o evento não pode ter dias fora de bimestre.
    """
    if evento.letivo == EventoLetivo.SIM:
        return True
    return evento.tipo_codigo not in TIPOS_PERMITIDOS_FORA_DO_BIMESTRE


def feriado_aceita_liberacao() -> bool:
    """Indica se a Liberação Excepcional permite evento letivo em feriado.

    Returns:
        True quando o feriado pode ser letivo com Liberação.
    """
    return True


def requer_validacao_de_datas(evento: Evento) -> bool:
    """Verifica se o evento passa pelas validações de data.

    Args:
        evento: Evento que está sendo validado.

    Returns:
        True quando bimestre, data travada, feriado, domingo e Liberação
        fora do período são conferidos.
    """
    if evento.tipo_codigo in TIPOS_ISENTOS_VALIDACAO_DATA:
        return False
    return not (
        evento.tipo_codigo == TipoEvento.FECHAMENTO_BIMESTRE
        and evento.eh_da_sme
    )


def _fora_de_bimestre(evento: Evento, calendario: Calendario) -> list[date]:
    """Lista os dias do evento que não estão em nenhum bimestre.

    Args:
        evento: Evento que está sendo validado.
        calendario: Calendário com os bimestres.

    Returns:
        Dias do evento fora de todos os bimestres, em ordem.
    """
    return [
        dia
        for dia in evento.dias()
        if not any(bimestre.cobre(dia) for bimestre in calendario.bimestres)
    ]


def _liberado(evento: Evento, calendario: Calendario, dia: date) -> bool:
    """Verifica se o dia tem Liberação Excepcional para o evento da UE.

    Args:
        evento: Evento que está sendo validado.
        calendario: Calendário com as Liberações cadastradas.
        dia: Dia conferido.

    Returns:
        True quando o evento é da UE, o dia está em bimestre e há
        Liberação da SME ou da mesma UE cobrindo o dia.
    """
    if not evento.eh_da_ue or not any(
        b.cobre(dia) for b in calendario.bimestres
    ):
        return False
    return any(
        outro.tipo_codigo == TipoEvento.LIBERACAO_EXCEPCIONAL
        and (outro.eh_da_sme or outro.ue_codigo == evento.ue_codigo)
        and outro.cobre(dia)
        for outro in calendario.eventos
    )


def _feriados_do_evento(evento: Evento, calendario: Calendario) -> list[date]:
    """Lista os dias do evento que são feriado.

    Args:
        evento: Evento que está sendo validado.
        calendario: Calendário com os eventos de Feriado e o catálogo fixo.

    Returns:
        Dias do evento que são feriado em algum dos anos que ele cobre.
    """
    anos = {dia.year for dia in evento.dias()}
    feriados = set().union(
        *(
            feriados_do_ano(ano, calendario.eventos, calendario.feriados_fixos)
            for ano in anos
        )
    )
    return [dia for dia in evento.dias() if dia in feriados]


def _domingos_do_evento(evento: Evento) -> list[date]:
    """Lista os domingos cobertos pelo evento.

    Args:
        evento: Evento que está sendo validado.

    Returns:
        Domingos entre o início e o fim do evento, em ordem.
    """
    return [dia for dia in evento.dias() if dia.weekday() == _DOMINGO]


def _verifica_liberacao_fora_do_periodo(
    evento: Evento, calendario: Calendario, data_confirmada: bool
) -> list[Violacao]:
    """Verifica se a Liberação Excepcional tem dias fora dos bimestres.

    Args:
        evento: Liberação Excepcional que está sendo validada.
        calendario: Calendário com os bimestres.
        data_confirmada: Se o usuário já confirmou manter as datas.

    Returns:
        Violação com os dias fora do bimestre, ou vazia quando não há dias
        ou o usuário já confirmou.
    """
    if data_confirmada:
        return []
    return _violacao_se_houver_datas(
        CodigoViolacao.LIBERACAO_FORA_DO_PERIODO,
        _fora_de_bimestre(evento, calendario),
    )


def _verifica_bimestre(
    evento: Evento, calendario: Calendario
) -> list[Violacao]:
    """Verifica se o evento tem dias fora de bimestre sem poder ter.

    Args:
        evento: Evento que está sendo validado.
        calendario: Calendário com os bimestres.

    Returns:
        ``FORA_DO_BIMESTRE`` para evento letivo, ``TIPO_FORA_DO_BIMESTRE``
        para tipo que não pode ficar fora do bimestre, ou vazia.
    """
    if not exige_datas_em_bimestres(evento):
        return []
    codigo = (
        CodigoViolacao.FORA_DO_BIMESTRE
        if evento.letivo == EventoLetivo.SIM
        else CodigoViolacao.TIPO_FORA_DO_BIMESTRE
    )
    return _violacao_se_houver_datas(
        codigo, _fora_de_bimestre(evento, calendario)
    )


def _datas_bloqueadas_pela_sme(
    evento: Evento, calendario: Calendario
) -> list[date]:
    """Lista os dias do evento cobertos por evento não letivo da SME.

    O Feriado da SME fica de fora porque é conferido como feriado.

    Args:
        evento: Evento que está sendo validado.
        calendario: Calendário com os eventos da SME.

    Returns:
        Dias do evento travados pela SME, em ordem.
    """
    travas = [
        outro
        for outro in calendario.eventos
        if outro.eh_da_sme
        and outro.tipo_codigo != TipoEvento.FERIADO
        and efeito_do_evento(outro) == Efeito.TIRA_O_DIA
    ]
    return [
        dia
        for dia in evento.dias()
        if any(trava.cobre(dia) for trava in travas)
    ]


def _verifica_data_travada(
    evento: Evento, calendario: Calendario
) -> list[Violacao]:
    """Verifica se o evento letivo da UE cai em dia travado pela SME.

    Args:
        evento: Evento que está sendo validado.
        calendario: Calendário com os eventos da SME e as Liberações.

    Returns:
        Violação com os dias travados sem Liberação Excepcional, ou vazia.
    """
    if evento.letivo != EventoLetivo.SIM or evento.eh_da_sme:
        return []
    return _violacao_se_houver_datas(
        CodigoViolacao.DATA_TRAVADA_PELA_SME,
        [
            dia
            for dia in _datas_bloqueadas_pela_sme(evento, calendario)
            if not _liberado(evento, calendario, dia)
        ],
    )


def _verifica_feriado_e_domingo(
    evento: Evento, calendario: Calendario
) -> list[Violacao]:
    """Verifica se o evento letivo cai em feriado ou domingo sem Liberação.

    Args:
        evento: Evento que está sendo validado.
        calendario: Calendário com bimestres, feriados e Liberações.

    Returns:
        Violações de feriado e de domingo com os dias recusados, ou vazia.
        Domingo fora de bimestre fica para a verificação de bimestre.
    """
    if evento.letivo != EventoLetivo.SIM:
        return []
    feriados = [
        dia
        for dia in _feriados_do_evento(evento, calendario)
        if not (
            feriado_aceita_liberacao() and _liberado(evento, calendario, dia)
        )
    ]
    domingos = [
        dia
        for dia in _domingos_do_evento(evento)
        if any(bimestre.cobre(dia) for bimestre in calendario.bimestres)
        and not _liberado(evento, calendario, dia)
    ]
    return _violacao_se_houver_datas(
        CodigoViolacao.FERIADO_SEM_LIBERACAO, feriados
    ) + _violacao_se_houver_datas(
        CodigoViolacao.DOMINGO_SEM_LIBERACAO, domingos
    )


def _verifica_fechamento(
    evento: Evento, calendario: Calendario
) -> list[Violacao]:
    """Verifica se o Fechamento da UE fica dentro do Fechamento da SME.

    Args:
        evento: Evento que está sendo validado.
        calendario: Calendário com os Fechamentos da SME.

    Returns:
        Violação com os dias fora do Fechamento da SME, ou vazia.
    """
    if (
        evento.tipo_codigo != TipoEvento.FECHAMENTO_BIMESTRE
        or not evento.eh_da_ue
    ):
        return []
    fechamentos_da_sme = [
        outro
        for outro in calendario.eventos
        if outro.tipo_codigo == TipoEvento.FECHAMENTO_BIMESTRE
        and outro.eh_da_sme
    ]
    return _violacao_se_houver_datas(
        CodigoViolacao.FECHAMENTO_FORA_DA_SME,
        [
            dia
            for dia in evento.dias()
            if not any(sme.cobre(dia) for sme in fechamentos_da_sme)
        ],
    )


def _verifica_letivo_do_tipo(evento: Evento) -> list[Violacao]:
    """Verifica se o letivo do evento combina com o tipo.

    Args:
        evento: Evento que está sendo validado.

    Returns:
        Violação quando o evento deveria ser letivo ou não letivo, ou
        vazia. Reunião Pedagógica é sempre não letiva.
    """
    if evento.tipo_codigo == TipoEvento.REUNIAO_PEDAGOGICA:
        if evento.letivo != EventoLetivo.NAO:
            return _violacao(CodigoViolacao.EVENTO_NAO_DEVE_SER_LETIVO)
        return []
    if letivo_coerente_com_tipo(evento.tipo_letivo, evento.letivo):
        return []
    if evento.tipo_letivo == EventoLetivo.SIM:
        return _violacao(CodigoViolacao.EVENTO_DEVE_SER_LETIVO)
    return _violacao(CodigoViolacao.EVENTO_NAO_DEVE_SER_LETIVO)


def _verificacoes_de_data(
    evento: Evento, data_confirmada: bool
) -> list[Callable[[Evento, Calendario], list[Violacao]]]:
    """Retorna as verificações de data que se aplicam ao evento.

    Args:
        evento: Evento que está sendo validado.
        data_confirmada: Se o usuário já confirmou manter uma Liberação
            Excepcional fora do período escolar.

    Returns:
        Verificações na ordem da spec; vazia quando o tipo não passa pelas
        validações de data.
    """
    if not requer_validacao_de_datas(evento):
        return []
    if evento.tipo_codigo == TipoEvento.LIBERACAO_EXCEPCIONAL:
        return [
            lambda ev, cal: _verifica_liberacao_fora_do_periodo(
                ev, cal, data_confirmada
            )
        ]
    return [
        _verifica_bimestre,
        _verifica_data_travada,
        _verifica_feriado_e_domingo,
    ]


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
        Violações encontradas, uma por código e na ordem da spec; vazia
        quando o evento é válido.
    """
    violacoes = _verifica_letivo_do_tipo(evento)
    if evento.inicio > evento.fim:
        return violacoes + _violacao(CodigoViolacao.EVENTO_INICIO_APOS_FIM)
    for verificacao in _verificacoes_de_data(evento, data_confirmada):
        violacoes += verificacao(evento, calendario)
    return violacoes + _verifica_fechamento(evento, calendario)


def exige_aprovacao(evento: Evento, calendario: Calendario) -> bool:
    """Verifica se o evento precisa de aprovação antes de valer.

    Abrange feriado, domingo e bloqueio da SME com autorização excepcional.

    Args:
        evento: Evento já validado.
        calendario: Calendário do evento, montado com a UE do evento.

    Returns:
        True quando o evento só foi aceito por Liberação Excepcional.
    """
    if (
        evento.letivo != EventoLetivo.SIM
        or evento.tipo_codigo == TipoEvento.LIBERACAO_EXCEPCIONAL
        or not requer_validacao_de_datas(evento)
    ):
        return False
    feriados = (
        _feriados_do_evento(evento, calendario)
        if feriado_aceita_liberacao()
        else []
    )
    bloqueios = _datas_bloqueadas_pela_sme(evento, calendario)
    dias = [*feriados, *_domingos_do_evento(evento), *bloqueios]
    return any(_liberado(evento, calendario, dia) for dia in dias)
