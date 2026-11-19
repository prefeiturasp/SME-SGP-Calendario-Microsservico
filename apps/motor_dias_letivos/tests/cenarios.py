"""Dados reais do calendário 95 (anual de 2026) para os testes do motor."""

from dataclasses import replace
from datetime import date

from apps.core.constants import (
    EventoLetivo,
    LocalOcorrencia,
    Periodo,
    TipoEvento,
)
from apps.motor_dias_letivos.dominio.dados_calendario import (
    Bimestre,
    Calendario,
    Evento,
    FeriadoFixo,
    TipoCalendario,
)

DRE = "108100"
UE = "094765"
OUTRA_UE = "019262"

TIPO_95 = TipoCalendario(
    id=95,
    ano_letivo=2026,
    periodo=Periodo.ANUAL,
    modalidade=1,
    semestre=None,
)

TESTES_BIMESTRES = (
    Bimestre(numero=1, inicio=date(2026, 2, 4), fim=date(2026, 4, 30)),
    Bimestre(numero=2, inicio=date(2026, 5, 4), fim=date(2026, 7, 4)),
    Bimestre(numero=3, inicio=date(2026, 7, 18), fim=date(2026, 9, 30)),
    Bimestre(numero=4, inicio=date(2026, 10, 1), fim=date(2026, 12, 22)),
)

FERIADOS_FIXOS = (
    FeriadoFixo(dia=1, mes=1, nome="Confraternização universal"),
    FeriadoFixo(dia=21, mes=4, nome="Tiradentes"),
    FeriadoFixo(dia=1, mes=5, nome="Dia do trabalhador"),
    FeriadoFixo(dia=7, mes=9, nome="Independência"),
    FeriadoFixo(dia=20, mes=11, nome="Consciência Negra (Municipal)"),
    FeriadoFixo(dia=25, mes=12, nome="Natal"),
)

_TIPOS: dict[int, tuple[int, int]] = {
    TipoEvento.CONSELHO_DE_CLASSE: (EventoLetivo.OPCIONAL, LocalOcorrencia.UE),
    TipoEvento.FECHAMENTO_BIMESTRE: (4, LocalOcorrencia.SME),
    TipoEvento.FERIADO: (EventoLetivo.NAO, LocalOcorrencia.SME),
    TipoEvento.FERIAS_DOCENTES: (EventoLetivo.NAO, LocalOcorrencia.SME),
    TipoEvento.ORGANIZACAO_ESCOLAR: (EventoLetivo.NAO, LocalOcorrencia.SME),
    TipoEvento.LIBERACAO_EXCEPCIONAL: (
        EventoLetivo.OPCIONAL,
        LocalOcorrencia.UE,
    ),
    TipoEvento.RECESSO: (EventoLetivo.NAO, LocalOcorrencia.SME),
    TipoEvento.RECREIO_NAS_FERIAS: (EventoLetivo.NAO, LocalOcorrencia.SME),
    TipoEvento.REPOSICAO_DE_AULA: (EventoLetivo.NAO, LocalOcorrencia.UE),
    TipoEvento.REPOSICAO_NO_RECESSO: (
        EventoLetivo.NAO,
        LocalOcorrencia.SME_UE,
    ),
    TipoEvento.REUNIAO_PEDAGOGICA: (
        EventoLetivo.OPCIONAL,
        LocalOcorrencia.SME_UE,
    ),
    TipoEvento.SONDAGEM: (4, LocalOcorrencia.SME),
}
REPOSICAO_DO_DIA = 14
SUSPENSAO_DE_ATIVIDADES = 21
OUTROS = 9
_TIPOS_SEM_CONSTANTE: dict[int, tuple[int, int]] = {
    REPOSICAO_DO_DIA: (EventoLetivo.SIM, LocalOcorrencia.UE),
    SUSPENSAO_DE_ATIVIDADES: (EventoLetivo.NAO, LocalOcorrencia.SME_UE),
    OUTROS: (EventoLetivo.OPCIONAL, LocalOcorrencia.TODOS),
}


def evento(
    tipo: int,
    inicio: date,
    fim: date | None = None,
    *,
    letivo: int | None = None,
    escopo: str = "UE",
    ue: str = UE,
    id: int | None = None,
) -> Evento:
    """Cria um evento do tipo informado.

    Args:
        tipo: Código do tipo de evento.
        inicio: Primeiro dia.
        fim: Último dia; sem fim, o evento tem um dia.
        letivo: Letivo do evento; sem valor, usa o do tipo.
        escopo: "SME", "DRE" ou "UE".
        ue: Código da UE, quando o escopo é UE.
        id: Id do evento; nulo no cadastro.

    Returns:
        Evento pronto para o motor.
    """
    tipo_letivo, local = {**_TIPOS, **_TIPOS_SEM_CONSTANTE}[tipo]
    return Evento(
        id=id,
        tipo_codigo=tipo,
        tipo_letivo=tipo_letivo,
        tipo_local_ocorrencia=local,
        letivo=tipo_letivo if letivo is None else letivo,
        inicio=inicio,
        fim=fim or inicio,
        dre_codigo=None if escopo == "SME" else DRE,
        ue_codigo=ue if escopo == "UE" else None,
    )


FERIADO_TIRADENTES = evento(
    TipoEvento.FERIADO, date(2026, 4, 21), escopo="SME"
)
FECHAMENTO_SME_1 = evento(
    TipoEvento.FECHAMENTO_BIMESTRE,
    date(2026, 4, 15),
    date(2026, 6, 12),
    letivo=0,
    escopo="SME",
)


def calendario(*eventos: Evento, ue: str | None = UE) -> Calendario:
    """Monta o calendário com os eventos informados."""
    return Calendario(
        tipo=TIPO_95,
        ue_codigo=ue,
        bimestres=TESTES_BIMESTRES,
        eventos=eventos,
        feriados_fixos=FERIADOS_FIXOS,
    )


def com_letivo(original: Evento, letivo: int) -> Evento:
    """Retorna uma cópia do evento com outro letivo."""
    return replace(original, letivo=letivo)
