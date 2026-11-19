"""Testes do serviço da visão do calendário."""

from django.test import SimpleTestCase

from apps.motor_dias_letivos.dominio.dados_calendario import Escopo
from apps.motor_dias_letivos.services import registrar_mudanca_no_calendario

ESCOPO_SME = Escopo(tipo_calendario_id=95, ue_codigo=None)
ESCOPO_UE = Escopo(tipo_calendario_id=95, ue_codigo="094765")


class RegistrarMudancaNoCalendarioTest(SimpleTestCase):
    """Confere os parâmetros aceitos por registrar_mudanca_no_calendario."""

    def test_aceita_criacao(self) -> None:
        """Aceita só o escopo depois da mudança."""
        registrar_mudanca_no_calendario(None, ESCOPO_UE)

    def test_aceita_exclusao(self) -> None:
        """Aceita só o escopo antes da mudança."""
        registrar_mudanca_no_calendario(ESCOPO_UE, None)

    def test_aceita_troca_de_escopo(self) -> None:
        """Aceita os dois escopos quando o registro muda de lugar."""
        registrar_mudanca_no_calendario(ESCOPO_SME, ESCOPO_UE)

    def test_aceita_escopos_iguais(self) -> None:
        """Aceita o mesmo escopo antes e depois."""
        registrar_mudanca_no_calendario(ESCOPO_UE, ESCOPO_UE)

    def test_recusa_os_dois_nulos(self) -> None:
        """Recusa a chamada sem nenhum escopo."""
        with self.assertRaises(ValueError):
            registrar_mudanca_no_calendario(None, None)
