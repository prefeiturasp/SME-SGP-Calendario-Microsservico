"""Testes dos códigos do motor de dias letivos."""

from django.test import SimpleTestCase

from apps.core.constants import TipoEvento
from apps.motor_dias_letivos.constants import (
    MENSAGENS_ERRO,
    MENSAGENS_VIOLACAO,
    ORDEM_AVISOS,
    TIPOS_ISENTOS_VALIDACAO_DATA,
    Aviso,
    CodigoErro,
    CodigoViolacao,
    Motivo,
)


class ConstantesMotorTest(SimpleTestCase):
    """Confere os códigos gravados na visão e devolvidos aos CRUDs."""

    def test_ordem_dos_avisos(self) -> None:
        """Mantém os avisos na ordem de prioridade."""
        self.assertEqual(
            ORDEM_AVISOS,
            (
                Aviso.BLOQUEADO_PELA_SME,
                Aviso.NAO_LETIVO_PREVALECEU,
                Aviso.DOMINGO_SEM_LIBERACAO,
                Aviso.FERIADO_SEM_LIBERACAO,
                Aviso.EVENTO_FORA_DO_BIMESTRE,
            ),
        )

    def test_isentos_de_validacao_de_data(self) -> None:
        """Isenta só Recesso e Reposição no Recesso (RN24)."""
        self.assertEqual(
            TIPOS_ISENTOS_VALIDACAO_DATA,
            {TipoEvento.RECESSO, TipoEvento.REPOSICAO_NO_RECESSO},
        )

    def test_motivos_aceitos_pelo_banco(self) -> None:
        """Usa os mesmos motivos do CHECK de visao_calendario_dia."""
        self.assertEqual(
            {str(motivo) for motivo in Motivo},
            {
                "DIA_UTIL",
                "FIM_DE_SEMANA",
                "FERIADO",
                "EVENTO_SME",
                "EVENTO_UE",
                "FORA_DE_BIMESTRE",
                "LIBERACAO_EXCEPCIONAL",
            },
        )

    def test_avisos_cabem_na_coluna(self) -> None:
        """Mantém motivos e avisos."""
        for codigo in [*Motivo, *Aviso]:
            self.assertLessEqual(len(codigo), 30, codigo)

    def test_toda_violacao_tem_mensagem(self) -> None:
        """Tem uma mensagem para cada código de violação."""
        self.assertEqual(set(MENSAGENS_VIOLACAO), set(CodigoViolacao))

    def test_todo_erro_tem_mensagem(self) -> None:
        """Tem uma mensagem para cada código de erro."""
        self.assertEqual(set(MENSAGENS_ERRO), set(CodigoErro))

    def test_mensagem_de_sobreposicao(self) -> None:
        """Preenche os números dos bimestres na mensagem."""
        mensagem = MENSAGENS_VIOLACAO[CodigoViolacao.SOBREPOSICAO].format(
            n=2, m=1
        )
        self.assertEqual(
            mensagem,
            "O início do 2º bimestre não pode ser anterior ao fim do 1º "
            "bimestre.",
        )

    def test_mensagem_de_ano_letivo(self) -> None:
        """Preenche o ano letivo nas duas datas."""
        mensagem = MENSAGENS_VIOLACAO[
            CodigoViolacao.FORA_DO_ANO_LETIVO
        ].format(n=4, ano=2026)
        self.assertEqual(
            mensagem,
            "4º bimestre: as datas devem estar entre 01/01/2026 e "
            "31/12/2026.",
        )

    def test_mensagem_de_periodo_sem_politica(self) -> None:
        """Preenche o período na mensagem de erro."""
        mensagem = MENSAGENS_ERRO[CodigoErro.PERIODO_SEM_POLITICA].format(
            periodo=3
        )
        self.assertEqual(mensagem, "Não há política para o período 3.")
