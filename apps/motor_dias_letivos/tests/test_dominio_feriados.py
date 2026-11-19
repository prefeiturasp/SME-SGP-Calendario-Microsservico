"""Testes dos feriados móveis e dos feriados do ano."""

from datetime import date

from django.test import SimpleTestCase

from apps.core.constants import TipoEvento
from apps.motor_dias_letivos.dominio.dados_calendario import FeriadoFixo
from apps.motor_dias_letivos.dominio.feriados import (
    feriados_do_ano,
    feriados_moveis,
)
from apps.motor_dias_letivos.tests.cenarios import (
    FERIADO_TIRADENTES,
    FERIADOS_FIXOS,
    evento,
)


def datas(feriados: list[tuple[date, str]]) -> list[date]:
    """Retorna só as datas dos feriados."""
    return [data for data, _nome in feriados]


class FeriadosMoveisTest(SimpleTestCase):
    """Confere os feriados calculados pela Páscoa."""

    def test_2025(self) -> None:
        """Calcula os móveis de 2025, com Páscoa em 20/04."""
        self.assertEqual(
            datas(feriados_moveis(2025)),
            [
                date(2025, 4, 18),
                date(2025, 4, 20),
                date(2025, 6, 19),
            ],
        )

    def test_2026(self) -> None:
        """Calcula os móveis de 2026, com Páscoa em 05/04."""
        self.assertEqual(
            datas(feriados_moveis(2026)),
            [
                date(2026, 4, 3),
                date(2026, 4, 5),
                date(2026, 6, 4),
            ],
        )

    def test_2027(self) -> None:
        """Calcula os móveis de 2027, com Páscoa em 28/03."""
        self.assertEqual(
            datas(feriados_moveis(2027)),
            [
                date(2027, 3, 26),
                date(2027, 3, 28),
                date(2027, 5, 27),
            ],
        )

    def test_correcoes_do_calculo_da_pascoa(self) -> None:
        """Aplica as duas correções do cálculo."""
        self.assertIn(date(1981, 4, 19), datas(feriados_moveis(1981)))
        self.assertIn(date(1954, 4, 18), datas(feriados_moveis(1954)))

    def test_nomes(self) -> None:
        """Nomeia os feriados móveis calculados."""
        self.assertEqual(
            [nome for _data, nome in feriados_moveis(2026)],
            [
                "Sexta-feira Santa",
                "Páscoa",
                "Corpus Christi",
            ],
        )


class FeriadosDoAnoTest(SimpleTestCase):
    """Confere a soma dos feriados de um ano."""

    def test_soma_eventos_catalogo_e_moveis(self) -> None:
        """Junta Feriado da SME e móveis."""
        recesso = evento(TipoEvento.FERIADO, date(2026, 7, 10), escopo="SME")
        feriados = feriados_do_ano(
            2026, [FERIADO_TIRADENTES, recesso], FERIADOS_FIXOS
        )
        self.assertIn(date(2026, 7, 10), feriados)
        self.assertIn(date(2026, 12, 25), feriados)
        self.assertNotIn(date(2026, 2, 16), feriados)
        self.assertEqual(len(feriados), 10)

    def test_ano_sem_eventos(self) -> None:
        """Usa eventos e feriados móveis em 2027, mesmo sem eventos."""
        feriados = feriados_do_ano(2027, [], FERIADOS_FIXOS)
        self.assertIn(date(2027, 4, 21), feriados)
        self.assertNotIn(date(2027, 2, 8), feriados)
        self.assertEqual(len(feriados), 9)

    def test_ignora_feriado_cadastrado_pela_ue(self) -> None:
        """Conta só eventos de Feriado da SME."""
        da_ue = evento(TipoEvento.FERIADO, date(2026, 8, 3))
        self.assertNotIn(date(2026, 8, 3), feriados_do_ano(2026, [da_ue], ()))

    def test_ignora_outros_tipos_de_evento(self) -> None:
        """Não trata outros eventos da SME como feriado."""
        recesso = evento(TipoEvento.RECESSO, date(2026, 7, 6), escopo="SME")
        self.assertNotIn(
            date(2026, 7, 6), feriados_do_ano(2026, [recesso], ())
        )

    def test_evento_de_feriado_de_varios_dias(self) -> None:
        """Conta cada dia do evento de Feriado dentro do ano."""
        virada = evento(
            TipoEvento.FERIADO,
            date(2026, 12, 31),
            date(2027, 1, 2),
            escopo="SME",
        )
        feriados = feriados_do_ano(2026, [virada], ())
        self.assertIn(date(2026, 12, 31), feriados)
        self.assertNotIn(date(2027, 1, 2), feriados)

    def test_feriado_fixo_inexistente_no_ano(self) -> None:
        """Ignora 29/02 em ano que não é bissexto."""
        bissexto = FeriadoFixo(dia=29, mes=2, nome="Teste")
        self.assertNotIn(
            date(2026, 3, 1), feriados_do_ano(2026, [], [bissexto])
        )
        self.assertIn(date(2028, 2, 29), feriados_do_ano(2028, [], [bissexto]))
