"""Políticas de calendário anual e semestral."""

from collections import Counter
from collections.abc import Iterable, Sequence
from datetime import date
from itertools import pairwise

from apps.core.constants import Periodo
from apps.core.excecoes import ErroDominio
from apps.motor_dias_letivos.constants import (
    MENSAGENS_ERRO,
    MENSAGENS_VIOLACAO,
    CodigoErro,
    CodigoViolacao,
)
from apps.motor_dias_letivos.dominio.dados_calendario import Bimestre
from apps.motor_dias_letivos.dominio.resultados import Violacao


def _violacao(codigo: CodigoViolacao, **valores: object) -> Violacao:
    return Violacao(
        codigo=codigo, mensagem=MENSAGENS_VIOLACAO[codigo].format(**valores)
    )


def _sobreposicao(anterior: Bimestre, posterior: Bimestre) -> Violacao:
    return _violacao(
        CodigoViolacao.SOBREPOSICAO, n=posterior.numero, m=anterior.numero
    )


def bimestres_sobrepostos(
    bimestres: Iterable[Bimestre],
) -> list[tuple[Bimestre, Bimestre]]:
    """Lista os bimestres que começam antes do fim do bimestre anterior.

    Cada bimestre é comparado com o de número imediatamente menor entre os
    informados. Começar no mesmo dia em que o anterior termina é aceito,
    como no legado. Números repetidos não são comparados entre si.

    Args:
        bimestres: Bimestres do calendário, em qualquer ordem.

    Returns:
        Pares ``(anterior, posterior)`` sobrepostos, em ordem de número.
    """
    ordenados = sorted(bimestres, key=lambda bimestre: bimestre.numero)
    return [
        (anterior, posterior)
        for anterior, posterior in pairwise(ordenados)
        if anterior.numero != posterior.numero
        and posterior.inicio < anterior.fim
    ]


class PoliticaCalendario:
    """Quantidade de bimestres, mínimo de dias e validação dos bimestres."""

    nome: str
    quantidade_bimestres: int
    minimo_dias_letivos: int

    def validar_bimestre(
        self,
        novo: Bimestre,
        existentes: Sequence[Bimestre],
        ano_letivo: int,
    ) -> list[Violacao]:
        """Valida um bimestre que está sendo salvo.

        Args:
            novo: Bimestre que está sendo incluído ou alterado.
            existentes: Demais bimestres do calendário, sem o que está em
                edição.
            ano_letivo: Ano letivo do tipo de calendário.

        Returns:
            Violações encontradas, na ordem dos códigos; vazia quando o
            bimestre é válido.
        """
        violacoes = self._fora_da_faixa([novo])
        if any(bimestre.numero == novo.numero for bimestre in existentes):
            violacoes.append(
                _violacao(CodigoViolacao.NUMERO_REPETIDO, n=novo.numero)
            )
        violacoes += self._datas_invalidas([novo], ano_letivo)
        violacoes += [
            _sobreposicao(anterior, posterior)
            for anterior, posterior in bimestres_sobrepostos(
                [*existentes, novo]
            )
            if novo in (anterior, posterior)
        ]
        return violacoes

    def validar_bimestres(
        self, bimestres: Sequence[Bimestre], ano_letivo: int
    ) -> list[Violacao]:
        """Valida todos os bimestres do calendário juntos.

        Cada bimestre com problema gera a sua violação; um número repetido
        é apontado uma vez só.

        Args:
            bimestres: Bimestres do calendário.
            ano_letivo: Ano letivo do tipo de calendário.

        Returns:
            Violações encontradas, na ordem dos códigos; vazia quando o
            conjunto é válido.
        """
        ordenados = sorted(bimestres, key=lambda bimestre: bimestre.numero)
        violacoes = self._fora_da_faixa(ordenados)
        repeticoes = Counter(bimestre.numero for bimestre in ordenados)
        violacoes += [
            _violacao(CodigoViolacao.NUMERO_REPETIDO, n=numero)
            for numero, vezes in repeticoes.items()
            if vezes > 1
        ]
        violacoes += self._datas_invalidas(ordenados, ano_letivo)
        violacoes += [
            _sobreposicao(anterior, posterior)
            for anterior, posterior in bimestres_sobrepostos(ordenados)
        ]
        if len(ordenados) != self.quantidade_bimestres:
            violacoes.append(
                _violacao(
                    CodigoViolacao.QUANTIDADE_DIFERENTE,
                    periodo=self.nome,
                    q=self.quantidade_bimestres,
                )
            )
        return violacoes

    def _fora_da_faixa(self, bimestres: Iterable[Bimestre]) -> list[Violacao]:
        return [
            _violacao(
                CodigoViolacao.NUMERO_FORA_DA_FAIXA,
                q=self.quantidade_bimestres,
            )
            for bimestre in bimestres
            if not 1 <= bimestre.numero <= self.quantidade_bimestres
        ]

    @staticmethod
    def _datas_invalidas(
        bimestres: Sequence[Bimestre], ano_letivo: int
    ) -> list[Violacao]:
        primeiro_dia = date(ano_letivo, 1, 1)
        ultimo_dia = date(ano_letivo, 12, 31)
        invertidos = [
            _violacao(CodigoViolacao.INICIO_APOS_FIM, n=bimestre.numero)
            for bimestre in bimestres
            if bimestre.inicio > bimestre.fim
        ]
        fora_do_ano = [
            _violacao(
                CodigoViolacao.FORA_DO_ANO_LETIVO,
                n=bimestre.numero,
                ano=ano_letivo,
            )
            for bimestre in bimestres
            if not primeiro_dia <= bimestre.inicio <= ultimo_dia
            or not primeiro_dia <= bimestre.fim <= ultimo_dia
        ]
        return invertidos + fora_do_ano


class PoliticaCalendarioAnual(PoliticaCalendario):
    """Calendário anual: 4 bimestres e mínimo de 200 dias letivos."""

    nome = "anual"
    quantidade_bimestres = 4
    minimo_dias_letivos = 200


class PoliticaCalendarioSemestral(PoliticaCalendario):
    """Calendário semestral: 2 bimestres e mínimo de 100 dias letivos."""

    nome = "semestral"
    quantidade_bimestres = 2
    minimo_dias_letivos = 100


_POLITICAS: dict[int, type[PoliticaCalendario]] = {
    Periodo.ANUAL: PoliticaCalendarioAnual,
    Periodo.SEMESTRAL: PoliticaCalendarioSemestral,
}


def obter_politica(periodo: int) -> PoliticaCalendario:
    """Retorna a política do período do tipo de calendário.

    Args:
        periodo: Período do tipo de calendário (anual ou semestral).

    Returns:
        Política com quantidade de bimestres e mínimo de dias.

    Raises:
        ErroDominio: ``PERIODO_SEM_POLITICA`` se o período não tem
            política.
    """
    politica = _POLITICAS.get(periodo)
    if politica is None:
        codigo = CodigoErro.PERIODO_SEM_POLITICA
        raise ErroDominio(
            codigo, MENSAGENS_ERRO[codigo].format(periodo=periodo)
        )
    return politica()
