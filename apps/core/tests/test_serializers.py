"""Testes dos serializers compartilhados do app core."""

from django.test import SimpleTestCase

from apps.core.serializers import RespostaPaginadaSerializer


class TestRespostaPaginadaSerializer(SimpleTestCase):
    """Valida o contrato genérico de respostas paginadas."""

    def test_aceita_lista_generica_e_metadados_da_paginacao(self) -> None:
        """Aceita itens de qualquer formato e metadados não negativos."""
        dados = {
            "itens": [{"codigo": 1}, {"codigo": 2}],
            "tamanho_pagina": 2,
            "total_itens": 10,
            "pagina_atual": 0,
        }

        serializer = RespostaPaginadaSerializer(data=dados)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data, dados)

    def test_rejeita_metadados_negativos(self) -> None:
        """Rejeita valores negativos nos metadados da paginação."""
        serializer = RespostaPaginadaSerializer(
            data={
                "itens": [],
                "tamanho_pagina": -1,
                "total_itens": -1,
                "pagina_atual": -1,
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            set(serializer.errors),
            {"tamanho_pagina", "total_itens", "pagina_atual"},
        )
