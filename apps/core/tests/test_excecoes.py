"""Testes do erro de domínio."""

from django.test import SimpleTestCase

from apps.core.excecoes import ErroDominio


class ErroDominioTest(SimpleTestCase):
    """Confere os dados pelo erro de domínio."""

    def test_guarda_codigo_e_mensagem(self) -> None:
        """Guarda o código e usa a mensagem como texto do erro."""
        erro = ErroDominio(
            "CALENDARIO_NAO_ENCONTRADO", "Tipo de calendário não encontrado."
        )
        self.assertEqual(erro.codigo, "CALENDARIO_NAO_ENCONTRADO")
        self.assertEqual(erro.mensagem, "Tipo de calendário não encontrado.")
        self.assertEqual(str(erro), "Tipo de calendário não encontrado.")

    def test_sem_detalhes_usa_lista_vazia(self) -> None:
        """Usa lista vazia quando não há detalhes."""
        erro = ErroDominio("VISAO_NAO_GERADA", "x")
        self.assertEqual(erro.detalhes, [])

    def test_guarda_os_detalhes(self) -> None:
        """Leva os detalhes que causaram o erro, em lista."""
        erro = ErroDominio("BIMESTRES_INVALIDOS", "x", detalhes=("a", "b"))
        self.assertEqual(erro.detalhes, ["a", "b"])

    def test_pode_ser_capturado_pelo_tipo(self) -> None:
        """Pode ser capturado como ErroDominio."""
        with self.assertRaises(ErroDominio):
            raise ErroDominio("CALENDARIO_SEM_BIMESTRES", "x")
