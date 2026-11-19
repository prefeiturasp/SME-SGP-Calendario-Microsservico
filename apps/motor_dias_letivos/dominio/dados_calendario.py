"""Dados que o motor de dias letivos recebe."""

from dataclasses import dataclass
from datetime import date, timedelta


def _dias_entre(inicio: date, fim: date) -> list[date]:
    return [
        inicio + timedelta(days=dia) for dia in range((fim - inicio).days + 1)
    ]


@dataclass(frozen=True)
class TipoCalendario:
    """Tipo do calendário: ano, duração e modalidade."""

    id: int
    ano_letivo: int
    periodo: int
    modalidade: int
    semestre: int | None


@dataclass(frozen=True)
class Bimestre:
    """Período escolar de um calendário, com datas inclusivas."""

    numero: int
    inicio: date
    fim: date

    def cobre(self, dia: date) -> bool:
        """Verifica se o dia está dentro do bimestre."""
        return self.inicio <= dia <= self.fim


@dataclass(frozen=True)
class Evento:
    """Evento do calendário com os dados do seu tipo.

    ``id`` é nulo quando o evento ainda está sendo cadastrado. Sem DRE e
    sem UE, o evento é da SME; só com DRE, é da DRE.
    """

    id: int | None
    tipo_codigo: int
    tipo_letivo: int
    tipo_local_ocorrencia: int
    letivo: int
    inicio: date
    fim: date
    dre_codigo: str | None
    ue_codigo: str | None

    @property
    def eh_da_sme(self) -> bool:
        """Indica evento da SME, sem DRE e sem UE."""
        return self.dre_codigo is None and self.ue_codigo is None

    @property
    def eh_da_ue(self) -> bool:
        """Indica evento de uma UE."""
        return self.ue_codigo is not None

    def dias(self) -> list[date]:
        """Lista os dias do evento; vazia se o início é depois do fim."""
        return _dias_entre(self.inicio, self.fim)

    def cobre(self, dia: date) -> bool:
        """Verifica se o dia está dentro do evento."""
        return self.inicio <= dia <= self.fim


@dataclass(frozen=True)
class FeriadoFixo:
    """Feriado que se repete todo ano no mesmo dia e mês."""

    dia: int
    mes: int
    nome: str


@dataclass(frozen=True)
class Calendario:
    """Tudo que o motor precisa para validar e classificar um calendário.

    ``ue_codigo`` nulo indica o calendário da SME. ``eventos`` traz os da
    SME e, quando há UE, também os dela; eventos da DRE não entram.
    """

    tipo: TipoCalendario
    ue_codigo: str | None
    bimestres: tuple[Bimestre, ...]
    eventos: tuple[Evento, ...]
    feriados_fixos: tuple[FeriadoFixo, ...]


@dataclass(frozen=True)
class Escopo:
    """Calendário afetado por uma mudança; UE nula indica a SME."""

    tipo_calendario_id: int
    ue_codigo: str | None
