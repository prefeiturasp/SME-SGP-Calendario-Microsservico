"""Testes dos models do app calendario."""

from django.db import models
from django.db.models.functions import Now
from django.test import SimpleTestCase

from apps.calendario.models import Modalidade, TipoCalendario


class TestModalidade(SimpleTestCase):
    """Valida o mapeamento do model de modalidade."""

    def test_mapeia_tabela_gerenciada(self) -> None:
        """Mapeia a tabela modalidade gerenciada pelo Django."""
        self.assertEqual(Modalidade._meta.db_table, "modalidade")
        self.assertTrue(Modalidade._meta.managed)

    def test_mapeia_campos(self) -> None:
        """Mapeia os campos conforme a tabela."""
        identificador = Modalidade._meta.get_field("id")
        descricao = Modalidade._meta.get_field("descricao")
        codigo_uuid = Modalidade._meta.get_field("codigo_uuid")

        self.assertIsInstance(identificador, models.BigAutoField)
        self.assertTrue(identificador.primary_key)
        self.assertIsInstance(descricao, models.CharField)
        self.assertEqual(descricao.max_length, 200)
        self.assertTrue(descricao.null)
        self.assertIsInstance(codigo_uuid, models.UUIDField)
        self.assertTrue(codigo_uuid.null)
        self.assertTrue(codigo_uuid.unique)


class TestTipoCalendario(SimpleTestCase):
    """Valida o mapeamento do model de tipo de calendário."""

    def test_mapeia_tabela_gerenciada(self) -> None:
        """Mapeia a tabela do schema calendario."""
        self.assertEqual(TipoCalendario._meta.db_table, "tipo_calendario")
        self.assertTrue(TipoCalendario._meta.managed)

    def test_mapeia_id_como_chave_primaria_automatica(self) -> None:
        """Usa identidade bigint como chave primária do ORM."""
        campo = TipoCalendario._meta.get_field("id")

        self.assertIsInstance(campo, models.BigAutoField)
        self.assertTrue(campo.primary_key)

    def test_mapeia_campos_obrigatorios(self) -> None:
        """Mapeia os campos obrigatórios conforme a tabela."""
        tipos = {
            "ano_letivo": models.IntegerField,
            "nome": models.CharField,
            "situacao": models.BooleanField,
            "criado_em": models.DateTimeField,
            "excluido": models.BooleanField,
            "migrado": models.BooleanField,
        }

        for nome, tipo in tipos.items():
            with self.subTest(nome=nome):
                campo = TipoCalendario._meta.get_field(nome)
                self.assertIsInstance(campo, tipo)
                self.assertFalse(campo.null)

    def test_mapeia_defaults(self) -> None:
        """Mapeia os valores padrão definidos no banco."""
        self.assertIs(
            TipoCalendario._meta.get_field("situacao").default,
            True,
        )
        self.assertIs(
            TipoCalendario._meta.get_field("excluido").default,
            False,
        )
        self.assertIs(
            TipoCalendario._meta.get_field("migrado").default,
            False,
        )
        self.assertIsInstance(
            TipoCalendario._meta.get_field("criado_em").db_default,
            Now,
        )

    def test_mapeia_campos_inteiros_nulaveis(self) -> None:
        """Mapeia os inteiros opcionais conforme a tabela."""
        nomes = ("semestre", "periodo")

        for nome in nomes:
            with self.subTest(nome=nome):
                campo = TipoCalendario._meta.get_field(nome)
                self.assertIsInstance(campo, models.IntegerField)
                self.assertTrue(campo.null)

    def test_mapeia_modalidade_como_chave_estrangeira(self) -> None:
        """Mapeia a modalidade pela coluna id_modalidade."""
        campo = TipoCalendario._meta.get_field("modalidade")

        self.assertIsInstance(campo, models.ForeignKey)
        self.assertEqual(campo.remote_field.model, Modalidade)
        self.assertEqual(campo.db_column, "id_modalidade")
        self.assertEqual(campo.remote_field.on_delete, models.DO_NOTHING)
        self.assertTrue(campo.null)

    def test_mapeia_campos_de_auditoria_nulaveis(self) -> None:
        """Mapeia os responsáveis de auditoria como opcionais."""
        limites = {
            "criado_rf": 100,
            "alterado_rf": 100,
            "criado_por": 200,
            "alterado_por": 200,
        }

        for nome, limite in limites.items():
            with self.subTest(nome=nome):
                campo = TipoCalendario._meta.get_field(nome)
                self.assertIsInstance(campo, models.CharField)
                self.assertEqual(campo.max_length, limite)
                self.assertTrue(campo.null)

        campo = TipoCalendario._meta.get_field("alterado_em")
        self.assertIsInstance(campo, models.DateTimeField)
        self.assertTrue(campo.null)

    def test_mapeia_nome_com_limite_de_cinquenta(self) -> None:
        """Mapeia o nome obrigatório com o tamanho definido no banco."""
        campo = TipoCalendario._meta.get_field("nome")

        self.assertIsInstance(campo, models.CharField)
        self.assertEqual(campo.max_length, 50)
        self.assertFalse(campo.null)

    def test_mapeia_codigo_uuid_unico_e_nulavel(self) -> None:
        """Mapeia o código UUID com unicidade e nulabilidade."""
        campo = TipoCalendario._meta.get_field("codigo_uuid")

        self.assertIsInstance(campo, models.UUIDField)
        self.assertTrue(campo.null)
        self.assertTrue(campo.unique)
