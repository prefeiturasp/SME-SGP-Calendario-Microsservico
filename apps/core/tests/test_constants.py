"""Testes dos códigos de domínio compartilhados."""

from django.test import SimpleTestCase

from apps.core.constants import (
    LETIVO_INFORMATIVOS,
    EventoLetivo,
    LocalOcorrencia,
    Periodo,
    StatusEvento,
    TipoEvento,
)


class TestConstantesCalendario(SimpleTestCase):
    """Protege os códigos persistidos e integrados com o legado."""

    def test_periodos(self) -> None:
        """Mantém os códigos dos períodos anual e semestral."""
        self.assertEqual(
            {item.name: item.value for item in Periodo},
            {"ANUAL": 1, "SEMESTRAL": 2},
        )

    def test_classificacoes_de_dia_letivo(self) -> None:
        """Mantém os códigos que classificam a contagem letiva."""
        self.assertEqual(
            {item.name: item.value for item in EventoLetivo},
            {"SIM": 1, "NAO": 2, "OPCIONAL": 3},
        )
        self.assertEqual(LETIVO_INFORMATIVOS, frozenset({0, 4}))

    def test_status_de_evento(self) -> None:
        """Mantém os códigos do fluxo de aprovação."""
        self.assertEqual(
            {item.name: item.value for item in StatusEvento},
            {
                "APROVADO": 1,
                "AGUARDANDO_APROVACAO": 2,
                "RECUSADO": 3,
            },
        )

    def test_locais_de_ocorrencia(self) -> None:
        """Mantém os códigos dos níveis que cadastram eventos."""
        self.assertEqual(
            {item.name: item.value for item in LocalOcorrencia},
            {
                "UE": 1,
                "DRE": 2,
                "SME": 3,
                "SME_UE": 4,
                "TODOS": 5,
            },
        )

    def test_tipos_de_evento_usados_nas_regras(self) -> None:
        """Mantém os códigos legados dos tipos de evento."""
        self.assertEqual(
            {item.name: item.value for item in TipoEvento},
            {
                "CONSELHO_DE_CLASSE": 1,
                "FECHAMENTO_BIMESTRE": 3,
                "FERIADO": 4,
                "LIBERACAO_EXCEPCIONAL": 6,
                "RECESSO": 11,
                "RECREIO_NAS_FERIAS": 12,
                "REPOSICAO_DE_AULA": 13,
                "REPOSICAO_NO_RECESSO": 15,
                "REUNIAO_PEDAGOGICA": 16,
                "SONDAGEM": 20,
            },
        )
