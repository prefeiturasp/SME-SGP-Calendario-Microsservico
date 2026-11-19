"""Códigos de domínio compartilhados entre os apps do calendário."""

from enum import IntEnum


class Periodo(IntEnum):
    """Duração do tipo de calendário."""

    ANUAL = 1
    SEMESTRAL = 2


class EventoLetivo(IntEnum):
    """Valores de ``letivo`` do evento e do tipo de evento."""

    SIM = 1
    NAO = 2
    OPCIONAL = 3


LETIVO_INFORMATIVOS = frozenset({0, 4})


class StatusEvento(IntEnum):
    """Situação de aprovação do evento."""

    APROVADO = 1
    AGUARDANDO_APROVACAO = 2
    RECUSADO = 3


class LocalOcorrencia(IntEnum):
    """Onde um tipo de evento pode ser cadastrado."""

    UE = 1
    DRE = 2
    SME = 3
    SME_UE = 4
    TODOS = 5


class TipoEvento(IntEnum):
    """Códigos de ``evento_tipo.codigo`` usados pelas regras."""

    CONSELHO_DE_CLASSE = 1
    FECHAMENTO_BIMESTRE = 3
    FERIADO = 4
    FERIAS_DOCENTES = 5
    LIBERACAO_EXCEPCIONAL = 6
    ORGANIZACAO_ESCOLAR = 8
    RECESSO = 11
    RECREIO_NAS_FERIAS = 12
    REPOSICAO_DE_AULA = 13
    REPOSICAO_NO_RECESSO = 15
    REUNIAO_PEDAGOGICA = 16
    SONDAGEM = 20
