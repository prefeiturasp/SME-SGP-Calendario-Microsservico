"""Testes das políticas de calendário e da validação dos bimestres."""

from datetime import date

from django.test import SimpleTestCase

from apps.core.constants import Periodo
from apps.core.excecoes import ErroDominio
from apps.motor_dias_letivos.constants import CodigoErro, CodigoViolacao
from apps.motor_dias_letivos.dominio.dados_calendario import Bimestre
from apps.motor_dias_letivos.dominio.politicas_calendario import (
    PoliticaCalendarioAnual,
    PoliticaCalendarioSemestral,
    bimestres_sobrepostos,
    obter_politica,
)

ANO = 2026

TESTE_BIMESTRES = (
    Bimestre(numero=1, inicio=date(2026, 2, 4), fim=date(2026, 4, 30)),
    Bimestre(numero=2, inicio=date(2026, 5, 4), fim=date(2026, 7, 4)),
    Bimestre(numero=3, inicio=date(2026, 7, 18), fim=date(2026, 9, 30)),
    Bimestre(numero=4, inicio=date(2026, 10, 1), fim=date(2026, 12, 22)),
)


def bimestre(numero: int, inicio: date, fim: date) -> Bimestre:
    """Cria um bimestre."""
    return Bimestre(numero=numero, inicio=inicio, fim=fim)


def codigos(violacoes: list) -> list[str]:
    """Retorna os códigos das violações, na ordem."""
    return [violacao.codigo for violacao in violacoes]


class ObterPoliticaTest(SimpleTestCase):
    """Confere a política escolhida pelo período do calendário (RN01)."""

    def test_anual(self) -> None:
        """Usa 4 bimestres e mínimo de 200 dias no anual."""
        politica = obter_politica(Periodo.ANUAL)
        self.assertIsInstance(politica, PoliticaCalendarioAnual)
        self.assertEqual(politica.quantidade_bimestres, 4)
        self.assertEqual(politica.minimo_dias_letivos, 200)

    def test_semestral(self) -> None:
        """Usa 2 bimestres e mínimo de 100 dias no semestral."""
        politica = obter_politica(Periodo.SEMESTRAL)
        self.assertIsInstance(politica, PoliticaCalendarioSemestral)
        self.assertEqual(politica.quantidade_bimestres, 2)
        self.assertEqual(politica.minimo_dias_letivos, 100)

    def test_periodo_sem_politica(self) -> None:
        """Recusa período que não tem política."""
        with self.assertRaises(ErroDominio) as contexto:
            obter_politica(3)
        self.assertEqual(
            contexto.exception.codigo, CodigoErro.PERIODO_SEM_POLITICA
        )
        self.assertEqual(
            contexto.exception.mensagem, "Não há política para o período 3."
        )


class ValidarBimestreTest(SimpleTestCase):
    """Valida um bimestre salvo de cada vez (RN02 a RN05)."""

    anual = PoliticaCalendarioAnual()
    semestral = PoliticaCalendarioSemestral()

    def test_primeiro_bimestre_salvo_sozinho(self) -> None:
        """Aceita o primeiro bimestre sem os demais."""
        self.assertEqual(
            self.anual.validar_bimestre(TESTE_BIMESTRES[0], [], ANO), []
        )

    def test_bimestre_valido_com_os_demais(self) -> None:
        """Aceita o 3º bimestre entre o 2º e o 4º."""
        violacoes = self.anual.validar_bimestre(
            TESTE_BIMESTRES[2], [*TESTE_BIMESTRES[:2], TESTE_BIMESTRES[3]], ANO
        )
        self.assertEqual(violacoes, [])

    def test_numero_zero(self) -> None:
        """Recusa bimestre de número 0."""
        violacoes = self.anual.validar_bimestre(
            bimestre(0, date(2026, 2, 4), date(2026, 4, 30)), [], ANO
        )
        self.assertEqual(
            codigos(violacoes), [CodigoViolacao.NUMERO_FORA_DA_FAIXA]
        )
        self.assertEqual(
            violacoes[0].mensagem, "O bimestre deve estar entre 1 e 4."
        )

    def test_numero_acima_da_quantidade_no_semestral(self) -> None:
        """Recusa o 3º bimestre no semestral."""
        violacoes = self.semestral.validar_bimestre(
            bimestre(3, date(2026, 2, 4), date(2026, 4, 30)), [], ANO
        )
        self.assertEqual(
            violacoes[0].mensagem, "O bimestre deve estar entre 1 e 2."
        )

    def test_numero_repetido(self) -> None:
        """Recusa um segundo período para o mesmo bimestre."""
        violacoes = self.anual.validar_bimestre(
            bimestre(2, date(2026, 5, 4), date(2026, 7, 4)),
            [TESTE_BIMESTRES[1]],
            ANO,
        )
        self.assertEqual(codigos(violacoes), [CodigoViolacao.NUMERO_REPETIDO])
        self.assertEqual(
            violacoes[0].mensagem, "Já existe período para o 2º bimestre."
        )

    def test_inicio_apos_fim(self) -> None:
        """Recusa início depois do fim."""
        violacoes = self.anual.validar_bimestre(
            bimestre(1, date(2026, 4, 30), date(2026, 2, 4)), [], ANO
        )
        self.assertEqual(codigos(violacoes), [CodigoViolacao.INICIO_APOS_FIM])
        self.assertEqual(
            violacoes[0].mensagem,
            "1º bimestre: a data de início não pode ser posterior à data de "
            "fim.",
        )

    def test_inicio_igual_ao_fim(self) -> None:
        """Aceita bimestre de um dia só."""
        violacoes = self.anual.validar_bimestre(
            bimestre(1, date(2026, 2, 4), date(2026, 2, 4)), [], ANO
        )
        self.assertEqual(violacoes, [])

    def test_ano_seguinte_recusado(self) -> None:
        """Recusa bimestre de 02/11/2026 a 20/02/2027 (ano civil, 18/11)."""
        violacoes = self.anual.validar_bimestre(
            bimestre(4, date(2026, 11, 2), date(2027, 2, 20)), [], ANO
        )
        self.assertEqual(
            codigos(violacoes), [CodigoViolacao.FORA_DO_ANO_LETIVO]
        )
        self.assertEqual(
            violacoes[0].mensagem,
            "4º bimestre: as datas devem estar entre 01/01/2026 e "
            "31/12/2026.",
        )

    def test_fim_no_ultimo_dia_do_ano(self) -> None:
        """Aceita fim em 31/12 do ano letivo."""
        violacoes = self.anual.validar_bimestre(
            bimestre(4, date(2026, 11, 2), date(2026, 12, 31)), [], ANO
        )
        self.assertEqual(violacoes, [])

    def test_inicio_em_2028_recusado(self) -> None:
        """Recusa datas de anos posteriores."""
        violacoes = self.anual.validar_bimestre(
            bimestre(4, date(2028, 1, 1), date(2028, 2, 1)), [], ANO
        )
        self.assertEqual(
            codigos(violacoes), [CodigoViolacao.FORA_DO_ANO_LETIVO]
        )

    def test_inicio_no_ano_anterior_recusado(self) -> None:
        """Recusa início antes de 01/01 do ano letivo."""
        violacoes = self.anual.validar_bimestre(
            bimestre(1, date(2025, 12, 31), date(2026, 4, 30)), [], ANO
        )
        self.assertEqual(
            codigos(violacoes), [CodigoViolacao.FORA_DO_ANO_LETIVO]
        )

    def test_segundo_sobreposto_ao_primeiro(self) -> None:
        """Recusa o 2º bimestre que começa antes do fim do 1º."""
        violacoes = self.anual.validar_bimestre(
            bimestre(2, date(2026, 4, 29), date(2026, 7, 4)),
            [TESTE_BIMESTRES[0]],
            ANO,
        )
        self.assertEqual(codigos(violacoes), [CodigoViolacao.SOBREPOSICAO])
        self.assertEqual(
            violacoes[0].mensagem,
            "O início do 2º bimestre não pode ser anterior ao fim do 1º "
            "bimestre.",
        )

    def test_novo_termina_depois_do_inicio_do_seguinte(self) -> None:
        """Recusa o 1º bimestre que termina depois do início do 2º."""
        violacoes = self.anual.validar_bimestre(
            bimestre(1, date(2026, 2, 4), date(2026, 5, 10)),
            [TESTE_BIMESTRES[1]],
            ANO,
        )
        self.assertEqual(
            violacoes[0].mensagem,
            "O início do 2º bimestre não pode ser anterior ao fim do 1º "
            "bimestre.",
        )

    def test_mesmo_dia_aceito(self) -> None:
        """Aceita o 2º começando no mesmo dia em que o 1º termina (RN05)."""
        violacoes = self.anual.validar_bimestre(
            bimestre(2, date(2026, 4, 30), date(2026, 7, 4)),
            [TESTE_BIMESTRES[0]],
            ANO,
        )
        self.assertEqual(violacoes, [])

    def test_compara_com_o_numero_menor_mais_proximo(self) -> None:
        """Compara o 3º com o 1º quando o 2º ainda não foi salvo."""
        violacoes = self.anual.validar_bimestre(
            bimestre(3, date(2026, 4, 1), date(2026, 9, 30)),
            [TESTE_BIMESTRES[0]],
            ANO,
        )
        self.assertEqual(
            violacoes[0].mensagem,
            "O início do 3º bimestre não pode ser anterior ao fim do 1º "
            "bimestre.",
        )

    def test_semestral_sobreposto(self) -> None:
        """Recusa sobreposição também no semestral."""
        violacoes = self.semestral.validar_bimestre(
            bimestre(2, date(2026, 5, 4), date(2026, 12, 23)),
            [bimestre(1, date(2026, 2, 5), date(2026, 6, 26))],
            ANO,
        )
        self.assertEqual(codigos(violacoes), [CodigoViolacao.SOBREPOSICAO])

    def test_violacoes_na_ordem_da_tabela(self) -> None:
        """Devolve as violações na ordem dos códigos da spec."""
        violacoes = self.anual.validar_bimestre(
            bimestre(5, date(2029, 3, 1), date(2029, 2, 1)), [], ANO
        )
        self.assertEqual(
            codigos(violacoes),
            [
                CodigoViolacao.NUMERO_FORA_DA_FAIXA,
                CodigoViolacao.INICIO_APOS_FIM,
                CodigoViolacao.FORA_DO_ANO_LETIVO,
            ],
        )

    def test_violacao_de_bimestre_sem_datas(self) -> None:
        """Deixa as datas vazias nas violações de bimestre."""
        violacoes = self.anual.validar_bimestre(
            bimestre(0, date(2026, 2, 4), date(2026, 4, 30)), [], ANO
        )
        self.assertEqual(violacoes[0].datas, ())


class ValidarBimestresTest(SimpleTestCase):
    """Valida todos os bimestres do calendário juntos (RN02 a RN06)."""

    anual = PoliticaCalendarioAnual()
    semestral = PoliticaCalendarioSemestral()

    def test_calendario_95_valido(self) -> None:
        """Aceita os bimestres reais do calendário 95."""
        self.assertEqual(self.anual.validar_bimestres(TESTE_BIMESTRES, ANO), [])

    def test_ordem_de_entrada_nao_importa(self) -> None:
        """Aceita os bimestres fora de ordem."""
        invertidos = tuple(reversed(TESTE_BIMESTRES))
        self.assertEqual(self.anual.validar_bimestres(invertidos, ANO), [])

    def test_quantidade_diferente_no_anual(self) -> None:
        """Recusa calendário anual com 3 bimestres."""
        violacoes = self.anual.validar_bimestres(TESTE_BIMESTRES[:3], ANO)
        self.assertEqual(
            codigos(violacoes), [CodigoViolacao.QUANTIDADE_DIFERENTE]
        )
        self.assertEqual(
            violacoes[0].mensagem,
            "Para calendário anual devem ser informados 4 bimestres.",
        )

    def test_quantidade_diferente_no_semestral(self) -> None:
        """Recusa calendário semestral com 3 bimestres."""
        violacoes = self.semestral.validar_bimestres(TESTE_BIMESTRES[:3], ANO)
        self.assertEqual(
            violacoes[-1].mensagem,
            "Para calendário semestral devem ser informados 2 bimestres.",
        )

    def test_sem_bimestres(self) -> None:
        """Recusa conjunto vazio só pela quantidade."""
        violacoes = self.anual.validar_bimestres((), ANO)
        self.assertEqual(
            codigos(violacoes), [CodigoViolacao.QUANTIDADE_DIFERENTE]
        )

    def test_numero_repetido_uma_vez_por_numero(self) -> None:
        """Aponta cada número repetido uma vez só."""
        repetidos = (*TESTE_BIMESTRES[:3], TESTE_BIMESTRES[2], TESTE_BIMESTRES[2])
        violacoes = self.anual.validar_bimestres(repetidos, ANO)
        self.assertEqual(
            [v.mensagem for v in violacoes if v.codigo == "NUMERO_REPETIDO"],
            ["Já existe período para o 3º bimestre."],
        )

    def test_calendario_14_sobreposto(self) -> None:
        """Recusa os bimestres reais do calendário 14 (semestral de 2020)."""
        bimestres = (
            bimestre(1, date(2020, 2, 5), date(2020, 6, 26)),
            bimestre(2, date(2020, 5, 4), date(2020, 12, 23)),
        )
        violacoes = self.semestral.validar_bimestres(bimestres, 2020)
        self.assertEqual(codigos(violacoes), [CodigoViolacao.SOBREPOSICAO])

    def test_uma_violacao_por_bimestre_com_problema(self) -> None:
        """Aponta cada bimestre com início depois do fim."""
        bimestres = (
            bimestre(1, date(2026, 4, 30), date(2026, 2, 4)),
            bimestre(2, date(2026, 7, 4), date(2026, 5, 4)),
        )
        violacoes = self.semestral.validar_bimestres(bimestres, ANO)
        self.assertEqual(
            [v.mensagem[:12] for v in violacoes],
            ["1º bimestre:", "2º bimestre:"],
        )

    def test_violacoes_na_ordem_da_tabela(self) -> None:
        """Devolve as violações na ordem dos códigos da spec."""
        bimestres = (
            bimestre(1, date(2026, 2, 4), date(2026, 4, 30)),
            bimestre(1, date(2026, 4, 1), date(2026, 3, 1)),
            bimestre(3, date(2026, 2, 1), date(2029, 2, 1)),
        )
        violacoes = self.semestral.validar_bimestres(bimestres, ANO)
        self.assertEqual(
            codigos(violacoes),
            [
                CodigoViolacao.NUMERO_FORA_DA_FAIXA,
                CodigoViolacao.NUMERO_REPETIDO,
                CodigoViolacao.INICIO_APOS_FIM,
                CodigoViolacao.FORA_DO_ANO_LETIVO,
                CodigoViolacao.SOBREPOSICAO,
                CodigoViolacao.QUANTIDADE_DIFERENTE,
            ],
        )


class BimestresSobrepostosTest(SimpleTestCase):
    """Confere a comparação de cada bimestre com o anterior (RN05)."""

    def test_sem_sobreposicao(self) -> None:
        """Não aponta nada no calendário 95."""
        self.assertEqual(bimestres_sobrepostos(TESTE_BIMESTRES), [])

    def test_devolve_o_par_em_ordem_de_numero(self) -> None:
        """Devolve o anterior e o posterior, nessa ordem."""
        primeiro = bimestre(1, date(2026, 2, 4), date(2026, 5, 10))
        segundo = TESTE_BIMESTRES[1]
        self.assertEqual(
            bimestres_sobrepostos([segundo, primeiro]), [(primeiro, segundo)]
        )

    def test_numeros_iguais_nao_sao_comparados(self) -> None:
        """Deixa o número repetido para NUMERO_REPETIDO."""
        repetido = bimestre(1, date(2026, 3, 1), date(2026, 3, 10))
        self.assertEqual(
            bimestres_sobrepostos([TESTE_BIMESTRES[0], repetido]), []
        )
