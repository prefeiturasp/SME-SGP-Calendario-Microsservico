"""Resultados da classificação e da validação do calendário."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ResultadoDia:
    """Decisão sobre uma data do calendário.

    ``evento_id`` é o evento que decidiu a data; ``bimestre`` é nulo fora
    de bimestre.
    """

    data: date
    dia_letivo: bool
    motivo: str
    evento_id: int | None
    bimestre: int | None
    aviso: str | None


@dataclass(frozen=True)
class ResultadoCalendario:
    """Dias classificados e totais de dias letivos do calendário.

    ``por_mes`` tem chave ``(ano, mês)``; ``por_bimestre`` e
    ``por_semestre`` têm o número do período como chave.
    """

    dias: tuple[ResultadoDia, ...]
    total: int
    minimo: int
    dias_faltantes: int
    por_mes: dict[tuple[int, int], int]
    por_bimestre: dict[int, int]
    por_semestre: dict[int, int]


@dataclass(frozen=True)
class Violacao:
    """Regra não atendida por um bimestre ou evento.

    ``datas`` traz os dias que causaram a recusa, quando se aplica.
    """

    codigo: str
    mensagem: str
    datas: tuple[date, ...] = ()
