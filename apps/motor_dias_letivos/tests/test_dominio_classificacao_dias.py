"""Testes da classificação das datas do calendário."""

from datetime import date

from django.test import SimpleTestCase

from apps.core.constants import EventoLetivo, TipoEvento
from apps.motor_dias_letivos.dominio.classificacao_dias import (
    Efeito,
    efeito_do_evento,
)
from apps.motor_dias_letivos.tests.cenarios import (
    OUTROS,
    REPOSICAO_DO_DIA,
    evento,
)

DIA = date(2026, 3, 10)


class EfeitoDoEventoTest(SimpleTestCase):
    """Confere o efeito de cada evento na contagem."""

    def test_letivo_sim_torna_letivo(self) -> None:
        """Torna o dia letivo com letivo 1."""
        self.assertEqual(
            efeito_do_evento(evento(REPOSICAO_DO_DIA, DIA)),
            Efeito.TORNA_LETIVO,
        )

    def test_letivo_nao_tira_o_dia(self) -> None:
        """Tira o dia com letivo 2."""
        outros = evento(OUTROS, DIA, letivo=EventoLetivo.NAO)
        self.assertEqual(efeito_do_evento(outros), Efeito.TIRA_O_DIA)

    def test_opcional_e_informativos_nao_alteram(self) -> None:
        """Não altera com letivo 0, 3 ou 4."""
        for letivo in (0, EventoLetivo.OPCIONAL, 4):
            with self.subTest(letivo=letivo):
                outros = evento(OUTROS, DIA, letivo=letivo)
                self.assertEqual(efeito_do_evento(outros), Efeito.NAO_ALTERA)

    def test_reuniao_pedagogica_sempre_tira(self) -> None:
        """Tira o dia na Reunião Pedagógica, qualquer que seja o letivo."""
        reuniao = evento(
            TipoEvento.REUNIAO_PEDAGOGICA, DIA, letivo=EventoLetivo.SIM
        )
        self.assertEqual(efeito_do_evento(reuniao), Efeito.TIRA_O_DIA)

    def test_recreio_nas_ferias_nao_altera(self) -> None:
        """Não altera no Recreio nas Férias, mesmo não letivo."""
        recreio = evento(TipoEvento.RECREIO_NAS_FERIAS, DIA, escopo="SME")
        self.assertEqual(efeito_do_evento(recreio), Efeito.NAO_ALTERA)

    def test_evento_da_dre_nao_altera(self) -> None:
        """Não altera com evento da DRE."""
        outros = evento(OUTROS, DIA, letivo=EventoLetivo.NAO, escopo="DRE")
        self.assertEqual(efeito_do_evento(outros), Efeito.NAO_ALTERA)

    def test_dv02_fechamento_tem_efeito_pelo_tipo(self) -> None:
        """Aplica a regra do tipo independentemente da letividade gravada."""
        for letivo in (EventoLetivo.SIM, EventoLetivo.NAO, 0, 4):
            with self.subTest(letivo=letivo):
                registro = evento(
                    TipoEvento.FECHAMENTO_BIMESTRE, DIA, letivo=letivo
                )
                self.assertEqual(efeito_do_evento(registro), Efeito.NAO_ALTERA)

    def test_dv04_reposicao_parcial_nao_cria_dia_letivo(self) -> None:
        """Impede que reposição parcial marcada como letiva acrescente dia."""
        reposicao = evento(
            TipoEvento.REPOSICAO_DE_AULA, DIA, letivo=EventoLetivo.SIM
        )
        self.assertEqual(efeito_do_evento(reposicao), Efeito.NAO_ALTERA)

    def test_dv05_conselho_tem_efeito_pelo_tipo(self) -> None:
        """Aplica a regra do tipo independentemente da letividade gravada."""
        for letivo in (EventoLetivo.SIM, EventoLetivo.NAO, 0, 4):
            with self.subTest(letivo=letivo):
                registro = evento(
                    TipoEvento.CONSELHO_DE_CLASSE, DIA, letivo=letivo
                )
                self.assertEqual(efeito_do_evento(registro), Efeito.TIRA_O_DIA)

    def test_dv06_sondagem_tem_efeito_pelo_tipo(self) -> None:
        """Aplica a regra do tipo independentemente da letividade gravada."""
        for letivo in (EventoLetivo.SIM, EventoLetivo.NAO, 0, 4):
            with self.subTest(letivo=letivo):
                registro = evento(TipoEvento.SONDAGEM, DIA, letivo=letivo)
                self.assertEqual(efeito_do_evento(registro), Efeito.NAO_ALTERA)
