"""Códigos e mensagens do motor de dias letivos."""

from enum import StrEnum

from apps.core.constants import TipoEvento

TIPOS_ISENTOS_VALIDACAO_DATA = frozenset(
    {TipoEvento.RECESSO, TipoEvento.REPOSICAO_NO_RECESSO}
)


class Motivo(StrEnum):
    """Motivo da decisão gravada para cada data da visão."""

    DIA_UTIL = "DIA_UTIL"
    FIM_DE_SEMANA = "FIM_DE_SEMANA"
    FERIADO = "FERIADO"
    EVENTO_SME = "EVENTO_SME"
    EVENTO_UE = "EVENTO_UE"
    FORA_DE_BIMESTRE = "FORA_DE_BIMESTRE"
    LIBERACAO_EXCEPCIONAL = "LIBERACAO_EXCEPCIONAL"


class Aviso(StrEnum):
    """Aviso gravado na data quando um evento não teve o efeito pedido."""

    BLOQUEADO_PELA_SME = "BLOQUEADO_PELA_SME"
    NAO_LETIVO_PREVALECEU = "NAO_LETIVO_PREVALECEU"
    DOMINGO_SEM_LIBERACAO = "DOMINGO_SEM_LIBERACAO"
    FERIADO_SEM_LIBERACAO = "FERIADO_SEM_LIBERACAO"
    EVENTO_FORA_DO_BIMESTRE = "EVENTO_FORA_DO_BIMESTRE"


ORDEM_AVISOS = (
    Aviso.BLOQUEADO_PELA_SME,
    Aviso.NAO_LETIVO_PREVALECEU,
    Aviso.DOMINGO_SEM_LIBERACAO,
    Aviso.FERIADO_SEM_LIBERACAO,
    Aviso.EVENTO_FORA_DO_BIMESTRE,
)


class CodigoViolacao(StrEnum):
    """Códigos das violações devolvidas pelas validações."""

    NUMERO_FORA_DA_FAIXA = "NUMERO_FORA_DA_FAIXA"
    NUMERO_REPETIDO = "NUMERO_REPETIDO"
    INICIO_APOS_FIM = "INICIO_APOS_FIM"
    FORA_DO_ANO_LETIVO = "FORA_DO_ANO_LETIVO"
    SOBREPOSICAO = "SOBREPOSICAO"
    QUANTIDADE_DIFERENTE = "QUANTIDADE_DIFERENTE"
    EVENTO_DEVE_SER_LETIVO = "EVENTO_DEVE_SER_LETIVO"
    EVENTO_NAO_DEVE_SER_LETIVO = "EVENTO_NAO_DEVE_SER_LETIVO"
    EVENTO_INICIO_APOS_FIM = "EVENTO_INICIO_APOS_FIM"
    LIBERACAO_FORA_DO_PERIODO = "LIBERACAO_FORA_DO_PERIODO"
    FORA_DO_BIMESTRE = "FORA_DO_BIMESTRE"
    DATA_TRAVADA_PELA_SME = "DATA_TRAVADA_PELA_SME"
    FERIADO_SEM_LIBERACAO = "FERIADO_SEM_LIBERACAO"
    DOMINGO_SEM_LIBERACAO = "DOMINGO_SEM_LIBERACAO"
    FECHAMENTO_FORA_DA_SME = "FECHAMENTO_FORA_DA_SME"


MENSAGENS_VIOLACAO = {
    CodigoViolacao.NUMERO_FORA_DA_FAIXA: (
        "O bimestre deve estar entre 1 e {q}."
    ),
    CodigoViolacao.NUMERO_REPETIDO: "Já existe período para o {n}º bimestre.",
    CodigoViolacao.INICIO_APOS_FIM: (
        "{n}º bimestre: a data de início não pode ser posterior à data de "
        "fim."
    ),
    CodigoViolacao.FORA_DO_ANO_LETIVO: (
        "{n}º bimestre: as datas devem estar entre 01/01/{ano} e "
        "31/12/{ano_seguinte}."
    ),
    CodigoViolacao.SOBREPOSICAO: (
        "O início do {n}º bimestre não pode ser anterior ao fim do {m}º "
        "bimestre."
    ),
    CodigoViolacao.QUANTIDADE_DIFERENTE: (
        "Para calendário {periodo} devem ser informados {q} bimestres."
    ),
    CodigoViolacao.EVENTO_DEVE_SER_LETIVO: (
        "O evento deve ser do tipo 'Letivo'."
    ),
    CodigoViolacao.EVENTO_NAO_DEVE_SER_LETIVO: (
        "O evento não deve ser do tipo 'Letivo'."
    ),
    CodigoViolacao.EVENTO_INICIO_APOS_FIM: (
        "A data de início não pode ser posterior à data de fim."
    ),
    CodigoViolacao.LIBERACAO_FORA_DO_PERIODO: (
        "Esta data é fora do período escolar. Confirme para manter a data."
    ),
    CodigoViolacao.FORA_DO_BIMESTRE: (
        "O evento letivo precisa estar dentro de um bimestre."
    ),
    CodigoViolacao.DATA_TRAVADA_PELA_SME: (
        "A SME definiu esta data como não letiva."
    ),
    CodigoViolacao.FERIADO_SEM_LIBERACAO: (
        "Evento letivo em feriado exige Liberação Excepcional."
    ),
    CodigoViolacao.DOMINGO_SEM_LIBERACAO: (
        "Evento letivo em domingo exige Liberação Excepcional."
    ),
    CodigoViolacao.FECHAMENTO_FORA_DA_SME: (
        "O fechamento da UE precisa estar dentro do fechamento definido "
        "pela SME."
    ),
}


class CodigoErro(StrEnum):
    """Códigos dos erros de domínio do calendário."""

    PERIODO_SEM_POLITICA = "PERIODO_SEM_POLITICA"
    CALENDARIO_NAO_ENCONTRADO = "CALENDARIO_NAO_ENCONTRADO"
    CALENDARIO_SEM_BIMESTRES = "CALENDARIO_SEM_BIMESTRES"
    BIMESTRES_INVALIDOS = "BIMESTRES_INVALIDOS"
    VISAO_NAO_GERADA = "VISAO_NAO_GERADA"


MENSAGENS_ERRO = {
    CodigoErro.PERIODO_SEM_POLITICA: (
        "Não há política para o período {periodo}."
    ),
    CodigoErro.CALENDARIO_NAO_ENCONTRADO: (
        "Tipo de calendário não encontrado."
    ),
    CodigoErro.CALENDARIO_SEM_BIMESTRES: (
        "O calendário não tem bimestres cadastrados."
    ),
    CodigoErro.BIMESTRES_INVALIDOS: (
        "Os bimestres do calendário são inválidos."
    ),
    CodigoErro.VISAO_NAO_GERADA: (
        "A visão deste calendário ainda não foi gerada."
    ),
}
