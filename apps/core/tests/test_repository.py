"""Testes do repositório base compartilhado."""

from uuid import uuid4

from django.db import IntegrityError, models
from django.test import TransactionTestCase

from apps.core.auditoria import UsuarioAuditoria
from apps.core.models import ModeloBase
from apps.core.repository import RepositorioBase


class RegistroTeste(ModeloBase):
    """Entidade concreta usada para validar o repositório base."""

    nome = models.CharField(max_length=100)

    class Meta:
        """Configura o model somente para a suíte de testes."""

        app_label = "core"


class TestRepositorioBase(TransactionTestCase):
    """Valida as operações comuns de persistência."""

    def setUp(self) -> None:
        """Cria o repositório e o usuário usados em cada teste."""
        self.repositorio = RepositorioBase(RegistroTeste)
        self.usuario = UsuarioAuditoria(nome="Maria", rf="1234567")

    def test_inserir_aplica_auditoria_de_criacao(self) -> None:
        """Persiste os dados e a autoria da criação."""
        codigo_uuid = uuid4()
        registro = self.repositorio.inserir(
            {"nome": "Evento", "codigo_uuid": codigo_uuid},
            self.usuario,
        )

        self.assertEqual(registro["nome"], "Evento")
        self.assertEqual(registro["codigo_uuid"], codigo_uuid)
        self.assertEqual(registro["criado_por"], "Maria")
        self.assertEqual(registro["criado_rf"], "1234567")
        self.assertFalse(registro["excluido"])

    def test_codigo_uuid_nao_pode_ser_repetido(self) -> None:
        """Rejeita dois registros com o mesmo UUID informado."""
        codigo_uuid = uuid4()
        self.repositorio.inserir(
            {"nome": "Primeiro", "codigo_uuid": codigo_uuid}
        )

        with self.assertRaises(IntegrityError):
            self.repositorio.inserir(
                {"nome": "Segundo", "codigo_uuid": codigo_uuid}
            )

    def test_listar_retorna_pagina_somente_com_registros_ativos(self) -> None:
        """Pagina registros ativos e informa o total antes do recorte."""
        self.repositorio.inserir({"nome": "Primeiro"})
        self.repositorio.inserir({"nome": "Segundo"})
        terceiro = self.repositorio.inserir({"nome": "Terceiro"})
        excluido = self.repositorio.inserir({"nome": "Excluído"})
        self.repositorio.excluir([excluido["id"]])

        resposta = self.repositorio.listar(
            pagina_atual=1,
            tamanho_pagina=2,
        )

        self.assertEqual(
            [registro["id"] for registro in resposta["itens"]],
            [terceiro["id"]],
        )
        self.assertEqual(resposta["tamanho_pagina"], 2)
        self.assertEqual(resposta["total_itens"], 3)
        self.assertEqual(resposta["pagina_atual"], 1)

    def test_listar_rejeita_parametros_negativos(self) -> None:
        """Rejeita página ou tamanho menores que zero."""
        with self.assertRaises(ValueError):
            self.repositorio.listar(pagina_atual=-1, tamanho_pagina=10)

        with self.assertRaises(ValueError):
            self.repositorio.listar(pagina_atual=0, tamanho_pagina=-1)

    def test_atualizar_aplica_dados_e_auditoria(self) -> None:
        """Atualiza o registro ativo e identifica o responsável."""
        registro = self.repositorio.inserir({"nome": "Anterior"})

        atualizado = self.repositorio.atualizar(
            registro["id"],
            {"nome": "Atualizado"},
            self.usuario,
        )

        self.assertEqual(atualizado["nome"], "Atualizado")
        self.assertEqual(atualizado["alterado_por"], "Maria")
        self.assertEqual(atualizado["alterado_rf"], "1234567")
        self.assertIsNotNone(atualizado["alterado_em"])

    def test_atualizar_rejeita_registro_excluido(self) -> None:
        """Não permite atualizar um registro excluído logicamente."""
        registro = self.repositorio.inserir({"nome": "Evento"})
        self.repositorio.excluir([registro["id"]])

        with self.assertRaises(RegistroTeste.DoesNotExist):
            self.repositorio.atualizar(
                registro["id"],
                {"nome": "Atualizado"},
            )

    def test_excluir_atualiza_lista_de_registros(self) -> None:
        """Marca os registros ativos e retorna a quantidade afetada."""
        primeiro = self.repositorio.inserir({"nome": "Primeiro"})
        segundo = self.repositorio.inserir({"nome": "Segundo"})

        quantidade = self.repositorio.excluir(
            [primeiro["id"], segundo["id"]],
            self.usuario,
        )

        self.assertEqual(quantidade, 2)
        registros = RegistroTeste._default_manager.order_by("id")
        self.assertTrue(all(registro.excluido for registro in registros))
        self.assertTrue(
            all(registro.alterado_por == "Maria" for registro in registros)
        )
