"""Testes da validação de evento."""

from datetime import date

from django.test import SimpleTestCase

from apps.core.constants import EventoLetivo, TipoEvento
from apps.motor_dias_letivos.constants import CodigoViolacao
from apps.motor_dias_letivos.dominio.dados_calendario import Evento
from apps.motor_dias_letivos.dominio.validacao_eventos import (
    exige_aprovacao,
    exige_datas_em_bimestres,
    feriado_aceita_liberacao,
    letivo_coerente_com_tipo,
    validar_evento,
)
from apps.motor_dias_letivos.tests.cenarios import (
    FECHAMENTO_SME_1,
    FERIADO_TIRADENTES,
    OUTRA_UE,
    OUTROS,
    REPOSICAO_DO_DIA,
    SUSPENSAO_DE_ATIVIDADES,
    calendario,
    evento,
)

SIM = EventoLetivo.SIM
NAO = EventoLetivo.NAO


def codigos(violacoes: list) -> list[str]:
    """Retorna os códigos das violações, na ordem."""
    return [violacao.codigo for violacao in violacoes]


def liberacao(
    inicio: date, fim: date | None = None, ue: str = "094765"
) -> Evento:
    """Cria uma Liberação Excepcional aprovada da UE."""
    return evento(TipoEvento.LIBERACAO_EXCEPCIONAL, inicio, fim, ue=ue)


class LetivoCoerenteComTipoTest(SimpleTestCase):
    """Confere a combinação do letivo do tipo com o do evento."""

    def test_tipo_letivo_exige_evento_letivo(self) -> None:
        """Aceita só Sim quando o tipo é letivo."""
        self.assertTrue(letivo_coerente_com_tipo(SIM, SIM))
        self.assertFalse(letivo_coerente_com_tipo(SIM, NAO))

    def test_tipo_nao_letivo_exige_evento_nao_letivo(self) -> None:
        """Aceita só Não quando o tipo não é letivo."""
        self.assertTrue(letivo_coerente_com_tipo(NAO, NAO))
        self.assertFalse(letivo_coerente_com_tipo(NAO, SIM))

    def test_demais_tipos_nao_restringem(self) -> None:
        """Aceita qualquer letivo em tipo opcional ou informativo."""
        self.assertTrue(letivo_coerente_com_tipo(EventoLetivo.OPCIONAL, SIM))
        self.assertTrue(letivo_coerente_com_tipo(4, NAO))


class ValidarEventoLetivoDoTipoTest(SimpleTestCase):
    """Confere o letivo do evento contra o tipo."""

    def test_evento_deve_ser_letivo(self) -> None:
        """Recusa Reposição do Dia não letiva."""
        reposicao = evento(REPOSICAO_DO_DIA, date(2026, 3, 9), letivo=NAO)
        violacoes = validar_evento(reposicao, calendario())
        self.assertEqual(
            codigos(violacoes), [CodigoViolacao.EVENTO_DEVE_SER_LETIVO]
        )
        self.assertEqual(
            violacoes[0].mensagem, "O evento deve ser do tipo 'Letivo'."
        )

    def test_evento_nao_deve_ser_letivo(self) -> None:
        """Recusa Reposição de Aula letiva, tipo não letivo."""
        reposicao = evento(
            TipoEvento.REPOSICAO_DE_AULA, date(2026, 3, 9), letivo=SIM
        )
        violacoes = validar_evento(reposicao, calendario())
        self.assertEqual(
            codigos(violacoes), [CodigoViolacao.EVENTO_NAO_DEVE_SER_LETIVO]
        )

    def test_reuniao_pedagogica_exige_nao_letivo(self) -> None:
        """Recusa Reunião Pedagógica que não seja não letiva."""
        reuniao = evento(
            TipoEvento.REUNIAO_PEDAGOGICA,
            date(2026, 3, 9),
            letivo=EventoLetivo.OPCIONAL,
        )
        violacoes = validar_evento(reuniao, calendario())
        self.assertEqual(
            codigos(violacoes), [CodigoViolacao.EVENTO_NAO_DEVE_SER_LETIVO]
        )

    def test_reuniao_pedagogica_nao_letiva_aceita(self) -> None:
        """Aceita Reunião Pedagógica não letiva."""
        reuniao = evento(
            TipoEvento.REUNIAO_PEDAGOGICA, date(2026, 3, 9), letivo=NAO
        )
        self.assertEqual(validar_evento(reuniao, calendario()), [])


class ValidarEventoDatasTest(SimpleTestCase):
    """Confere início, fim e bimestres do evento."""

    def test_inicio_apos_fim(self) -> None:
        """Recusa início depois do fim e não confere os dias."""
        invertido = evento(
            REPOSICAO_DO_DIA, date(2026, 7, 10), date(2026, 7, 6)
        )
        violacoes = validar_evento(invertido, calendario())
        self.assertEqual(
            codigos(violacoes), [CodigoViolacao.EVENTO_INICIO_APOS_FIM]
        )
        self.assertEqual(
            violacoes[0].mensagem,
            "A data de início não pode ser posterior à data de fim.",
        )

    def test_evento_letivo_dentro_do_bimestre(self) -> None:
        """Aceita evento letivo de vários dias dentro do bimestre."""
        reposicao = evento(
            REPOSICAO_DO_DIA, date(2026, 3, 9), date(2026, 3, 13)
        )
        self.assertEqual(validar_evento(reposicao, calendario()), [])

    def test_evento_letivo_fora_do_bimestre(self) -> None:
        """Recusa os dias do evento letivo fora de bimestre."""
        reposicao = evento(
            REPOSICAO_DO_DIA, date(2026, 7, 3), date(2026, 7, 6)
        )
        violacoes = validar_evento(reposicao, calendario())
        self.assertEqual(codigos(violacoes), [CodigoViolacao.FORA_DO_BIMESTRE])
        self.assertEqual(
            violacoes[0].datas,
            (date(2026, 7, 5), date(2026, 7, 6)),
        )
        self.assertEqual(
            violacoes[0].mensagem,
            "O evento letivo precisa estar dentro de um bimestre.",
        )

    def test_evento_em_bimestres_continuos(self) -> None:
        """Aceita evento que passa de um bimestre para o seguinte."""
        reposicao = evento(
            REPOSICAO_DO_DIA, date(2026, 9, 28), date(2026, 10, 2)
        )
        self.assertEqual(validar_evento(reposicao, calendario()), [])

    def test_dv01_tipo_nao_permitido_fora_do_bimestre(self) -> None:
        """Recusa Outros não letivo no recesso."""
        outros = evento(OUTROS, date(2026, 7, 3), date(2026, 7, 6), letivo=NAO)
        self.assertTrue(exige_datas_em_bimestres(outros))
        violacoes = validar_evento(outros, calendario())
        self.assertEqual(
            codigos(violacoes), [CodigoViolacao.TIPO_FORA_DO_BIMESTRE]
        )
        self.assertEqual(
            violacoes[0].datas, (date(2026, 7, 5), date(2026, 7, 6))
        )
        self.assertEqual(
            violacoes[0].mensagem,
            "Fora do bimestre só podem ser cadastrados Férias Docentes, "
            "Recreio nas Férias, Recesso e Organização.",
        )

    def test_dv01_tipos_permitidos_fora_do_bimestre(self) -> None:
        """Aceita fora do bimestre os tipos da reunião, mais Feriado."""
        for tipo in (
            TipoEvento.FERIAS_DOCENTES,
            TipoEvento.ORGANIZACAO_ESCOLAR,
            TipoEvento.RECREIO_NAS_FERIAS,
            TipoEvento.FERIADO,
        ):
            with self.subTest(tipo=tipo):
                sme = evento(
                    tipo, date(2026, 1, 2), date(2026, 1, 30), escopo="SME"
                )
                self.assertFalse(exige_datas_em_bimestres(sme))
                self.assertEqual(validar_evento(sme, calendario()), [])

    def test_dv01_fechamento_segue_a_janela_da_sme(self) -> None:
        """Não exige bimestre do Fechamento, que segue a SME."""
        fechamento = evento(
            TipoEvento.FECHAMENTO_BIMESTRE, date(2026, 7, 3), date(2026, 7, 6)
        )
        self.assertFalse(exige_datas_em_bimestres(fechamento))

    def test_dv01_tipo_permitido_letivo_fora_do_bimestre(self) -> None:
        """Recusa evento letivo fora do bimestre mesmo de tipo permitido."""
        organizacao = evento(
            TipoEvento.ORGANIZACAO_ESCOLAR,
            date(2026, 1, 26),
            letivo=SIM,
            escopo="SME",
        )
        self.assertTrue(exige_datas_em_bimestres(organizacao))
        self.assertIn(
            CodigoViolacao.FORA_DO_BIMESTRE,
            codigos(validar_evento(organizacao, calendario())),
        )


class ValidarEventoIsentosTest(SimpleTestCase):
    """Confere os tipos que não passam pelas validações de data."""

    def test_recesso_isento(self) -> None:
        """Aceita Recesso fora de bimestre e em domingo."""
        recesso = evento(
            TipoEvento.RECESSO,
            date(2026, 7, 5),
            date(2026, 7, 17),
            escopo="SME",
        )
        self.assertEqual(validar_evento(recesso, calendario()), [])

    def test_reposicao_no_recesso_isenta(self) -> None:
        """Não confere bimestre nem domingo na Reposição no Recesso."""
        reposicao = evento(
            TipoEvento.REPOSICAO_NO_RECESSO,
            date(2026, 7, 5),
            date(2026, 7, 6),
            letivo=SIM,
        )
        self.assertEqual(
            codigos(validar_evento(reposicao, calendario())),
            [CodigoViolacao.EVENTO_NAO_DEVE_SER_LETIVO],
        )

    def test_fechamento_da_sme_isento(self) -> None:
        """Aceita Fechamento da SME fora de bimestre."""
        fechamento = evento(
            TipoEvento.FECHAMENTO_BIMESTRE,
            date(2026, 7, 5),
            date(2026, 7, 10),
            letivo=SIM,
            escopo="SME",
        )
        self.assertEqual(validar_evento(fechamento, calendario()), [])


class ValidarEventoLiberacaoTest(SimpleTestCase):
    """Confere a Liberação Excepcional fora do período."""

    def test_liberacao_fora_do_periodo_sem_confirmacao(self) -> None:
        """Pede confirmação da data fora de bimestre."""
        fora = liberacao(date(2026, 7, 6), date(2026, 7, 7))
        violacoes = validar_evento(fora, calendario())
        self.assertEqual(
            codigos(violacoes), [CodigoViolacao.LIBERACAO_FORA_DO_PERIODO]
        )
        self.assertEqual(
            violacoes[0].datas, (date(2026, 7, 6), date(2026, 7, 7))
        )

    def test_liberacao_fora_do_periodo_confirmada(self) -> None:
        """Aceita a data fora de bimestre depois da confirmação."""
        fora = liberacao(date(2026, 7, 6))
        self.assertEqual(
            validar_evento(fora, calendario(), data_confirmada=True), []
        )

    def test_liberacao_em_domingo_e_feriado(self) -> None:
        """Não confere domingo nem feriado na própria Liberação."""
        domingo = liberacao(date(2026, 4, 19), date(2026, 4, 21))
        self.assertEqual(
            validar_evento(domingo, calendario(FERIADO_TIRADENTES)), []
        )


class ValidarEventoTravadoPelaSmeTest(SimpleTestCase):
    """Confere a data que a SME tirou."""

    def test_data_travada_por_evento_nao_letivo_da_sme(self) -> None:
        """Recusa evento letivo da UE em dia que a SME tirou."""
        suspensao = evento(
            SUSPENSAO_DE_ATIVIDADES,
            date(2026, 3, 10),
            date(2026, 3, 11),
            escopo="SME",
        )
        reposicao = evento(
            REPOSICAO_DO_DIA, date(2026, 3, 9), date(2026, 3, 12)
        )
        violacoes = validar_evento(reposicao, calendario(suspensao))
        self.assertEqual(
            codigos(violacoes), [CodigoViolacao.DATA_TRAVADA_PELA_SME]
        )
        self.assertEqual(
            violacoes[0].datas, (date(2026, 3, 10), date(2026, 3, 11))
        )

    def test_reuniao_pedagogica_da_sme_trava(self) -> None:
        """Trata Reunião Pedagógica da SME como dia tirado."""
        reuniao = evento(
            TipoEvento.REUNIAO_PEDAGOGICA,
            date(2026, 3, 10),
            letivo=NAO,
            escopo="SME",
        )
        reposicao = evento(REPOSICAO_DO_DIA, date(2026, 3, 10))
        self.assertEqual(
            codigos(validar_evento(reposicao, calendario(reuniao))),
            [CodigoViolacao.DATA_TRAVADA_PELA_SME],
        )

    def test_suspensao_da_dre_nao_trava(self) -> None:
        """Ignora evento não letivo da DRE."""
        suspensao = evento(
            SUSPENSAO_DE_ATIVIDADES, date(2026, 3, 10), escopo="DRE"
        )
        reposicao = evento(REPOSICAO_DO_DIA, date(2026, 3, 10))
        self.assertEqual(validar_evento(reposicao, calendario(suspensao)), [])

    def test_recreio_da_sme_nao_trava(self) -> None:
        """Ignora Recreio nas Férias da SME, que não altera o dia."""
        recreio = evento(
            TipoEvento.RECREIO_NAS_FERIAS, date(2026, 3, 10), escopo="SME"
        )
        reposicao = evento(REPOSICAO_DO_DIA, date(2026, 3, 10))
        self.assertEqual(validar_evento(reposicao, calendario(recreio)), [])

    def test_evento_da_sme_nao_e_travado(self) -> None:
        """Não aplica a trava a evento da própria SME."""
        suspensao = evento(
            SUSPENSAO_DE_ATIVIDADES, date(2026, 3, 10), escopo="SME"
        )
        outros = evento(OUTROS, date(2026, 3, 10), letivo=SIM, escopo="SME")
        self.assertEqual(validar_evento(outros, calendario(suspensao)), [])


class ValidarEventoFeriadoEDomingoTest(SimpleTestCase):
    """Confere feriado e domingo sem Liberação Excepcional."""

    def test_feriado_sem_liberacao(self) -> None:
        """Recusa evento letivo que passa por feriado."""
        reposicao = evento(
            REPOSICAO_DO_DIA, date(2026, 4, 20), date(2026, 4, 22)
        )
        violacoes = validar_evento(reposicao, calendario(FERIADO_TIRADENTES))
        self.assertEqual(
            codigos(violacoes), [CodigoViolacao.FERIADO_SEM_LIBERACAO]
        )
        self.assertEqual(violacoes[0].datas, (date(2026, 4, 21),))

    def test_carnaval_depende_de_cadastro(self) -> None:
        """Só bloqueia Carnaval quando a SME registra a suspensão."""
        data = date(2026, 2, 16)
        reposicao = evento(REPOSICAO_DO_DIA, data)
        suspensao = evento(SUSPENSAO_DE_ATIVIDADES, data, escopo="SME")
        self.assertEqual(validar_evento(reposicao, calendario()), [])
        self.assertEqual(
            codigos(validar_evento(reposicao, calendario(suspensao))),
            [CodigoViolacao.DATA_TRAVADA_PELA_SME],
        )

    def test_dv03_liberacao_da_sme_supera_bloqueio(self) -> None:
        """Aceita a reposição com autorização excepcional da SME."""
        data = date(2026, 3, 10)
        suspensao = evento(SUSPENSAO_DE_ATIVIDADES, data, escopo="SME")
        autorizacao = evento(
            TipoEvento.LIBERACAO_EXCEPCIONAL, data, escopo="SME"
        )
        reposicao = evento(REPOSICAO_DO_DIA, data)
        cal = calendario(suspensao, autorizacao)
        self.assertEqual(validar_evento(reposicao, cal), [])
        self.assertTrue(exige_aprovacao(reposicao, cal))

    def test_dv03_autorizacao_nao_dispensa_bimestre(self) -> None:
        """Recusa o evento letivo autorizado fora do período escolar."""
        data = date(2026, 1, 25)
        autorizacao = evento(
            TipoEvento.LIBERACAO_EXCEPCIONAL, data, escopo="SME"
        )
        reposicao = evento(REPOSICAO_DO_DIA, data)
        self.assertIn(
            CodigoViolacao.FORA_DO_BIMESTRE,
            codigos(validar_evento(reposicao, calendario(autorizacao))),
        )

    def test_dv03_feriado_com_liberacao_letivo(self) -> None:
        """Aceita feriado com Liberação e exige aprovação."""
        reposicao = evento(REPOSICAO_DO_DIA, date(2026, 4, 21))
        cal = calendario(FERIADO_TIRADENTES, liberacao(date(2026, 4, 21)))
        self.assertTrue(feriado_aceita_liberacao())
        self.assertEqual(validar_evento(reposicao, cal), [])
        self.assertTrue(exige_aprovacao(reposicao, cal))

    def test_liberacao_de_outra_ue_nao_vale(self) -> None:
        """Exige a Liberação da mesma UE do evento."""
        reposicao = evento(REPOSICAO_DO_DIA, date(2026, 4, 21))
        cal = calendario(
            FERIADO_TIRADENTES, liberacao(date(2026, 4, 21), ue=OUTRA_UE)
        )
        self.assertEqual(
            codigos(validar_evento(reposicao, cal)),
            [CodigoViolacao.FERIADO_SEM_LIBERACAO],
        )

    def test_liberacao_em_outro_dia_nao_vale(self) -> None:
        """Exige a Liberação no próprio dia do feriado."""
        reposicao = evento(
            REPOSICAO_DO_DIA, date(2026, 4, 20), date(2026, 4, 21)
        )
        cal = calendario(FERIADO_TIRADENTES, liberacao(date(2026, 4, 20)))
        self.assertEqual(
            codigos(validar_evento(reposicao, cal)),
            [CodigoViolacao.FERIADO_SEM_LIBERACAO],
        )

    def test_domingo_no_inicio_sem_liberacao(self) -> None:
        """Recusa evento letivo que começa em domingo."""
        reposicao = evento(
            REPOSICAO_DO_DIA, date(2026, 3, 8), date(2026, 3, 9)
        )
        violacoes = validar_evento(reposicao, calendario())
        self.assertEqual(
            codigos(violacoes), [CodigoViolacao.DOMINGO_SEM_LIBERACAO]
        )
        self.assertEqual(violacoes[0].datas, (date(2026, 3, 8),))
        self.assertEqual(
            violacoes[0].mensagem,
            "Evento letivo em domingo exige Liberação Excepcional.",
        )

    def test_domingo_no_fim_sem_liberacao(self) -> None:
        """Recusa evento letivo que termina em domingo."""
        reposicao = evento(
            REPOSICAO_DO_DIA, date(2026, 3, 14), date(2026, 3, 15)
        )
        self.assertEqual(
            validar_evento(reposicao, calendario())[0].datas,
            (date(2026, 3, 15),),
        )

    def test_domingo_no_meio_exige_liberacao(self) -> None:
        """Exige liberação também para o domingo no meio do evento."""
        reposicao = evento(
            REPOSICAO_DO_DIA, date(2026, 3, 7), date(2026, 3, 9)
        )
        domingo = date(2026, 3, 8)
        violacoes = validar_evento(reposicao, calendario())
        self.assertEqual(
            codigos(violacoes), [CodigoViolacao.DOMINGO_SEM_LIBERACAO]
        )
        self.assertEqual(violacoes[0].datas, (domingo,))
        cal = calendario(liberacao(domingo))
        self.assertEqual(validar_evento(reposicao, cal), [])
        self.assertTrue(exige_aprovacao(reposicao, cal))

    def test_domingo_com_liberacao(self) -> None:
        """Aceita domingo com Liberação e exige aprovação."""
        reposicao = evento(REPOSICAO_DO_DIA, date(2026, 3, 8))
        cal = calendario(liberacao(date(2026, 3, 8)))
        self.assertEqual(validar_evento(reposicao, cal), [])
        self.assertTrue(exige_aprovacao(reposicao, cal))

    def test_evento_nao_letivo_em_feriado(self) -> None:
        """Não confere feriado em evento não letivo."""
        outros = evento(OUTROS, date(2026, 4, 21), letivo=NAO)
        self.assertEqual(
            validar_evento(outros, calendario(FERIADO_TIRADENTES)), []
        )

    def test_evento_da_sme_em_feriado_sem_liberacao(self) -> None:
        """Recusa evento letivo da SME em feriado: a Liberação é da UE."""
        outros = evento(OUTROS, date(2026, 4, 21), letivo=SIM, escopo="SME")
        self.assertEqual(
            codigos(validar_evento(outros, calendario(FERIADO_TIRADENTES))),
            [CodigoViolacao.FERIADO_SEM_LIBERACAO],
        )


class ValidarEventoFechamentoTest(SimpleTestCase):
    """Confere o Fechamento da UE dentro do da SME."""

    def test_fechamento_da_ue_dentro_do_da_sme(self) -> None:
        """Aceita o Fechamento da UE contido no da SME."""
        fechamento = evento(
            TipoEvento.FECHAMENTO_BIMESTRE,
            date(2026, 4, 20),
            date(2026, 4, 30),
            letivo=0,
        )
        self.assertEqual(
            validar_evento(fechamento, calendario(FECHAMENTO_SME_1)), []
        )

    def test_fechamento_da_ue_fora_do_da_sme(self) -> None:
        """Recusa os dias do Fechamento da UE fora do da SME."""
        fechamento = evento(
            TipoEvento.FECHAMENTO_BIMESTRE,
            date(2026, 6, 11),
            date(2026, 6, 15),
            letivo=0,
        )
        violacoes = validar_evento(fechamento, calendario(FECHAMENTO_SME_1))
        self.assertEqual(
            codigos(violacoes), [CodigoViolacao.FECHAMENTO_FORA_DA_SME]
        )
        self.assertEqual(
            violacoes[0].datas,
            (date(2026, 6, 13), date(2026, 6, 14), date(2026, 6, 15)),
        )

    def test_fechamento_da_ue_sem_fechamento_da_sme(self) -> None:
        """Recusa o Fechamento da UE quando a SME não definiu nenhum."""
        fechamento = evento(
            TipoEvento.FECHAMENTO_BIMESTRE, date(2026, 4, 20), letivo=0
        )
        self.assertEqual(
            codigos(validar_evento(fechamento, calendario())),
            [CodigoViolacao.FECHAMENTO_FORA_DA_SME],
        )

    def test_fechamento_da_ue_em_dois_fechamentos_da_sme(self) -> None:
        """Aceita o Fechamento da UE coberto por dois da SME seguidos."""
        segundo = evento(
            TipoEvento.FECHAMENTO_BIMESTRE,
            date(2026, 6, 13),
            date(2026, 9, 14),
            letivo=0,
            escopo="SME",
        )
        fechamento = evento(
            TipoEvento.FECHAMENTO_BIMESTRE,
            date(2026, 6, 11),
            date(2026, 6, 15),
            letivo=0,
        )
        self.assertEqual(
            validar_evento(fechamento, calendario(FECHAMENTO_SME_1, segundo)),
            [],
        )


class ValidarEventoGeralTest(SimpleTestCase):
    """Confere a ordem das violações e a concomitância."""

    def test_violacoes_na_ordem_da_tabela(self) -> None:
        """Devolve uma violação por código, na ordem da spec."""
        suspensao = evento(
            SUSPENSAO_DE_ATIVIDADES, date(2026, 4, 30), escopo="SME"
        )
        reposicao = evento(
            REPOSICAO_DO_DIA, date(2026, 4, 19), date(2026, 7, 5), letivo=NAO
        )
        reposicao_letiva = evento(
            REPOSICAO_DO_DIA, date(2026, 4, 19), date(2026, 7, 5)
        )
        cal = calendario(FERIADO_TIRADENTES, suspensao)
        self.assertEqual(
            codigos(validar_evento(reposicao, cal)),
            [
                CodigoViolacao.EVENTO_DEVE_SER_LETIVO,
                CodigoViolacao.TIPO_FORA_DO_BIMESTRE,
            ],
        )
        self.assertEqual(
            codigos(validar_evento(reposicao_letiva, cal)),
            [
                CodigoViolacao.FORA_DO_BIMESTRE,
                CodigoViolacao.DATA_TRAVADA_PELA_SME,
                CodigoViolacao.FERIADO_SEM_LIBERACAO,
                CodigoViolacao.DOMINGO_SEM_LIBERACAO,
            ],
        )

    def test_dv07_concomitancia_nao_validada(self) -> None:
        """Aceita evento no mesmo dia de um Feriado."""
        outros = evento(OUTROS, date(2026, 4, 21), letivo=NAO)
        mesmo_tipo = evento(
            TipoEvento.FERIADO, date(2026, 4, 21), escopo="SME"
        )
        cal = calendario(FERIADO_TIRADENTES)
        self.assertEqual(validar_evento(outros, cal), [])
        self.assertEqual(validar_evento(mesmo_tipo, cal), [])


class ExigeAprovacaoTest(SimpleTestCase):
    """Confere quando o evento precisa de aprovação."""

    def test_evento_comum_nao_exige(self) -> None:
        """Não exige aprovação de evento letivo em dia útil."""
        reposicao = evento(REPOSICAO_DO_DIA, date(2026, 3, 9))
        self.assertFalse(exige_aprovacao(reposicao, calendario()))

    def test_evento_nao_letivo_nao_exige(self) -> None:
        """Não exige aprovação de evento não letivo em feriado."""
        outros = evento(OUTROS, date(2026, 4, 21), letivo=NAO)
        cal = calendario(FERIADO_TIRADENTES, liberacao(date(2026, 4, 21)))
        self.assertFalse(exige_aprovacao(outros, cal))

    def test_isento_nao_exige(self) -> None:
        """Não exige aprovação de Reposição no Recesso em domingo."""
        reposicao = evento(
            TipoEvento.REPOSICAO_NO_RECESSO, date(2026, 3, 8), letivo=SIM
        )
        cal = calendario(liberacao(date(2026, 3, 8)))
        self.assertFalse(exige_aprovacao(reposicao, cal))

    def test_liberacao_nao_exige(self) -> None:
        """Não exige aprovação da própria Liberação Excepcional."""
        propria = liberacao(date(2026, 3, 8))
        self.assertFalse(exige_aprovacao(propria, calendario(propria)))
