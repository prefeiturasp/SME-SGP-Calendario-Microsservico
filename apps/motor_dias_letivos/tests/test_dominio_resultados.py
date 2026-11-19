"""Testes dos resultados do motor de dias letivos."""

from dataclasses import FrozenInstanceError
from datetime import date

from django.test import SimpleTestCase

from apps.motor_dias_letivos.constants import Motivo
from apps.motor_dias_letivos.dominio.resultados import (
    ResultadoCalendario,
    ResultadoDia,
    Violacao,
)


class ResultadosImutaveisTest(SimpleTestCase):
    """Garante que os resultados do motor não mudam depois de criados."""

    def test_resultado_dia_imutavel(self) -> None:
        """Recusa alterar a decisão de uma data."""
        dia = ResultadoDia(
            data=date(2026, 2, 16),
            dia_letivo=False,
            motivo=Motivo.FERIADO,
            evento_id=None,
            bimestre=1,
            aviso=None,
        )
        with self.assertRaises(FrozenInstanceError):
            dia.dia_letivo = True  # type: ignore[misc]

    def test_resultado_calendario_imutavel(self) -> None:
        """Recusa alterar o total do calendário."""
        resultado = ResultadoCalendario(
            dias=(),
            total=0,
            minimo=200,
            dias_faltantes=200,
            por_mes={},
            por_bimestre={},
            por_semestre={},
        )
        with self.assertRaises(FrozenInstanceError):
            resultado.total = 1  # type: ignore[misc]

    def test_violacao_imutavel(self) -> None:
        """Recusa trocar o código da violação."""
        violacao = Violacao(codigo="FORA_DO_BIMESTRE", mensagem="x")
        with self.assertRaises(FrozenInstanceError):
            violacao.codigo = "OUTRO"  # type: ignore[misc]

    def test_violacao_sem_datas_tem_tupla_vazia(self) -> None:
        """Usa tupla vazia quando a violação não tem datas."""
        violacao = Violacao(codigo="NUMERO_REPETIDO", mensagem="x")
        self.assertEqual(violacao.datas, ())
