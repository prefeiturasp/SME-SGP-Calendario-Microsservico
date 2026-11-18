"""Testes dos repositórios do app calendario."""

from django.test import TransactionTestCase

from apps.calendario.models import Modalidade, TipoCalendario
from apps.calendario.repository import (
    RepositorioModalidade,
    RepositorioTipoCalendario,
)
from apps.core.auditoria import UsuarioAuditoria
from apps.core.repository import RepositorioBase


class TestRepositorioTipoCalendario(TransactionTestCase):
    """Valida o CRUD persistente de tipos de calendário."""

    def setUp(self) -> None:
        """Cria dependências usadas nos testes."""
        self.repositorio = RepositorioTipoCalendario()
        self.usuario = UsuarioAuditoria(nome="Maria", rf="1234567")
        self.modalidade = Modalidade.objects.create(descricao="Fundamental")

    def test_herda_repositorio_base_com_modelo_configurado(self) -> None:
        """Reutiliza as operações comuns com o model correto."""
        self.assertIsInstance(self.repositorio, RepositorioBase)
        self.assertIs(self.repositorio.modelo, TipoCalendario)

    def test_executa_crud_herdado(self) -> None:
        """Inclui, consulta, lista, altera e exclui logicamente."""
        criado = self.repositorio.inserir(
            {
                "ano_letivo": 2027,
                "nome": "Calendário 2027",
                "modalidade": self.modalidade,
                "periodo": 1,
            },
            self.usuario,
        )

        encontrado = self.repositorio.obter_por_id(criado["id"])
        pagina = self.repositorio.listar(0, 10)
        atualizado = self.repositorio.atualizar(
            criado["id"],
            {"nome": "Calendário atualizado"},
            self.usuario,
        )
        quantidade = self.repositorio.excluir(
            [criado["id"]],
            self.usuario,
        )

        self.assertEqual(encontrado["nome"], "Calendário 2027")
        self.assertEqual(pagina["total_itens"], 1)
        self.assertEqual(atualizado["nome"], "Calendário atualizado")
        self.assertEqual(quantidade, 1)
        with self.assertRaises(TipoCalendario.DoesNotExist):
            self.repositorio.obter_por_id(criado["id"])


class TestRepositorioModalidade(TransactionTestCase):
    """Valida a listagem paginada de modalidades."""

    def setUp(self) -> None:
        """Cria o repositório usado nos testes."""
        self.repositorio = RepositorioModalidade()

    def test_listar_retorna_pagina_ordenada(self) -> None:
        """Retorna o recorte e os metadados da paginação."""
        Modalidade.objects.create(descricao="Primeira")
        Modalidade.objects.create(descricao="Segunda")
        terceira = Modalidade.objects.create(descricao="Terceira")

        resposta = self.repositorio.listar(1, 2)

        self.assertEqual(
            [registro["id"] for registro in resposta["itens"]],
            [terceira.id],
        )
        self.assertEqual(resposta["tamanho_pagina"], 2)
        self.assertEqual(resposta["total_itens"], 3)
        self.assertEqual(resposta["pagina_atual"], 1)

    def test_listar_rejeita_parametros_negativos(self) -> None:
        """Rejeita página ou tamanho menores que zero."""
        with self.assertRaises(ValueError):
            self.repositorio.listar(-1, 10)

        with self.assertRaises(ValueError):
            self.repositorio.listar(0, -1)
