Calendário Escolar
==================

O calendário é a base de tudo o que é registrado no SGP: nenhuma
atividade existe sem estar vinculada a um calendário.

Calendário escolar
------------------

Conjunto de eventos escolares vinculado a um ano civil, que determina o
funcionamento da escola durante o ano.

- Calendário anual: no mínimo 200 dias letivos.
- Calendário semestral: no mínimo 100 dias letivos.
- Não existe máximo de dias letivos.

Tipos de calendário
-------------------

Cada tipo é anual ou semestral e se vincula a uma modalidade de ensino.
Exemplos:

- Calendário 2026 para Ensino Fundamental e Médio.
- Calendário 1º Semestre 2024 para EJA Regular.

Modalidades com regras próprias: Fundamental, Médio, Infantil, EJA,
CELP e CIEJA. As diferenças entre calendários anuais e semestrais são
tratadas por políticas de domínio (ADR-002).

Eventos
-------

Registro do que acontece em um dia do calendário. Todo evento tem:

- **Tipo**: usado para validar dias letivos e contar os dias do
  calendário.
- **Nome**: texto amigável exibido no calendário. Exemplo: evento do
  tipo Reposição com o nome "Festa da Primavera".

Eventos podem ser letivos ou não letivos.

Hierarquia
----------

O calendário tem camadas: SME, DRE e UE. Cada camada superior obriga as
inferiores a seguir os eventos que criou. Se a SME define um dia como
não letivo, nenhum calendário de DRE ou UE pode torná-lo letivo.

Entidades do legado
-------------------

No SME-NovoSGP, as entidades do calendário ficam em
``src/SME.SGP.Dominio/Entidades/``:

- ``TipoCalendario``
- ``PeriodoEscolar``
- ``Evento``
- ``EventoTipo``
- ``FeriadoCalendario``
