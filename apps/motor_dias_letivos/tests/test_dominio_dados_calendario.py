"""Testes dos dados de entrada do motor de dias letivos."""

from dataclasses import FrozenInstanceError
from datetime import date

from django.test import SimpleTestCase

from apps.core.constants import (
    EventoLetivo,
    LocalOcorrencia,
    Periodo,
    TipoEvento,
)
from apps.motor_dias_letivos.dominio.dados_calendario import (
    Bimestre,
    Calendario,
    Escopo,
    Evento,
    FeriadoFixo,
    TipoCalendario,
)


def criar_tipo() -> TipoCalendario:
    """Cria um tipo de calendário anual de 2026."""
    return TipoCalendario(
        id=95,
        ano_letivo=2026,
        periodo=Periodo.ANUAL,
        modalidade=1,
        semestre=None,
    )


def criar_evento() -> Evento:
    """Cria um evento letivo de uma UE."""
    return Evento(
        id=None,
        tipo_codigo=TipoEvento.REPOSICAO_DE_AULA,
        tipo_letivo=EventoLetivo.NAO,
        tipo_local_ocorrencia=LocalOcorrencia.UE,
        letivo=EventoLetivo.SIM,
        inicio=date(2026, 3, 7),
        fim=date(2026, 3, 7),
        dre_codigo="108100",
        ue_codigo="094765",
    )


class DadosCalendarioImutaveisTest(SimpleTestCase):
    """Garante que as entradas do motor não mudam depois de criadas."""

    def test_tipo_calendario_imutavel(self) -> None:
        """Recusa alterar um campo do tipo de calendário."""
        tipo = criar_tipo()
        with self.assertRaises(FrozenInstanceError):
            tipo.periodo = Periodo.SEMESTRAL  # type: ignore[misc]

    def test_bimestre_imutavel(self) -> None:
        """Recusa alterar a data de fim do bimestre."""
        bimestre = Bimestre(
            numero=1, inicio=date(2026, 2, 4), fim=date(2026, 4, 30)
        )
        with self.assertRaises(FrozenInstanceError):
            bimestre.fim = date(2026, 5, 1)  # type: ignore[misc]

    def test_evento_imutavel(self) -> None:
        """Recusa alterar o letivo do evento."""
        evento = criar_evento()
        with self.assertRaises(FrozenInstanceError):
            evento.letivo = EventoLetivo.NAO  # type: ignore[misc]

    def test_feriado_fixo_imutavel(self) -> None:
        """Recusa alterar o dia do feriado fixo."""
        feriado = FeriadoFixo(dia=25, mes=12, nome="Natal")
        with self.assertRaises(FrozenInstanceError):
            feriado.dia = 24  # type: ignore[misc]

    def test_calendario_imutavel(self) -> None:
        """Recusa trocar os eventos do calendário."""
        calendario = Calendario(
            tipo=criar_tipo(),
            ue_codigo=None,
            bimestres=(),
            eventos=(criar_evento(),),
            feriados_fixos=(),
        )
        with self.assertRaises(FrozenInstanceError):
            calendario.eventos = ()  # type: ignore[misc]

    def test_escopo_imutavel(self) -> None:
        """Recusa trocar a UE do escopo."""
        escopo = Escopo(tipo_calendario_id=95, ue_codigo=None)
        with self.assertRaises(FrozenInstanceError):
            escopo.ue_codigo = "094765"  # type: ignore[misc]


class EscopoValoresTest(SimpleTestCase):
    """Confere a igualdade e o uso de escopos em conjuntos."""

    def test_escopos_iguais_sao_iguais(self) -> None:
        """Compara escopos pelo valor dos campos."""
        self.assertEqual(
            Escopo(tipo_calendario_id=95, ue_codigo="094765"),
            Escopo(tipo_calendario_id=95, ue_codigo="094765"),
        )

    def test_escopo_pode_ser_usado_em_conjunto(self) -> None:
        """Permite tirar escopos repetidos com set."""
        escopos = {
            Escopo(tipo_calendario_id=95, ue_codigo=None),
            Escopo(tipo_calendario_id=95, ue_codigo=None),
        }
        self.assertEqual(len(escopos), 1)
