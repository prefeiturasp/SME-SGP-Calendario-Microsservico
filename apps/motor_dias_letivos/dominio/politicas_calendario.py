"""Políticas de calendário anual e semestral."""

from collections.abc import Sequence

from apps.motor_dias_letivos.dominio.dados_calendario import Bimestre
from apps.motor_dias_letivos.dominio.resultados import Violacao


class PoliticaCalendario:
    """Quantidade de bimestres, mínimo de dias e validação dos bimestres."""

    quantidade_bimestres: int
    minimo_dias_letivos: int

    def validar_bimestre(
        self,
        novo: Bimestre,
        existentes: Sequence[Bimestre],
        ano_letivo: int,
    ) -> list[Violacao]:
        """Valida um bimestre que está sendo salvo.

        Args:
            novo: Bimestre que está sendo incluído ou alterado.
            existentes: Demais bimestres do calendário, sem o que está em
                edição.
            ano_letivo: Ano letivo do tipo de calendário.

        Returns:
            Violações encontradas; vazia quando o bimestre é válido.
        """
        raise NotImplementedError

    def validar_bimestres(
        self, bimestres: Sequence[Bimestre], ano_letivo: int
    ) -> list[Violacao]:
        """Valida todos os bimestres do calendário juntos.

        Args:
            bimestres: Bimestres do calendário.
            ano_letivo: Ano letivo do tipo de calendário.

        Returns:
            Violações encontradas; vazia quando o conjunto é válido.
        """
        raise NotImplementedError


def obter_politica(periodo: int) -> PoliticaCalendario:
    """Retorna a política do período do tipo de calendário.

    Args:
        periodo: Período do tipo de calendário (anual ou semestral).

    Returns:
        Política com quantidade de bimestres e mínimo de dias.

    Raises:
        ErroDominio: ``PERIODO_SEM_POLITICA`` se o período não tem
            política.
    """
    raise NotImplementedError
