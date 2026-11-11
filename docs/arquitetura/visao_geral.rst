Visão geral
===========

Objetivo
--------

Gerenciar o calendário escolar da Rede Municipal de Ensino: definição,
manutenção e disponibilização dos calendários letivos para SME, COPED,
DRE, UE, professores e sistemas do ecossistema SGP.

O domínio contempla calendários, períodos escolares (bimestres,
trimestres e semestres), eventos, feriados, pontos facultativos,
fechamentos, reaberturas, cálculo de dias letivos e auditoria das
alterações.

Papel na arquitetura
--------------------

Este repositório é o backend do domínio. Ele implementa as regras de
negócio e é o único que acessa o banco ``SGP_CALENDARIO_DB``.

.. code-block:: text

   SME-SGP-Calendario-Microfrontend (ReactJS)
           |
           v
   SME-SGP-Calendario-BFF (Django)
           |  API Key
           v
   SME-SGP-Calendario-Microsservico ---> SGP_CALENDARIO_DB
           |                                  |
           |                        Transactional Outbox
           |                                  v
           |                         RabbitMQ (Celery)
           |                                  |
           v                                  v
   Consumidores REST             SyncWorker ---> SGP_DB (legado)

Componentes do domínio
----------------------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Componente
     - Responsabilidade
   * - SME-SGP-Calendario-Microfrontend
     - Interface do domínio, integrada ao portal NOVO-SGP.
   * - SME-SGP-Calendario-BFF
     - Agregação e adaptação de APIs para o frontend.
   * - SME-SGP-Calendario-Microsservico
     - Regras de negócio e persistência do domínio (este repositório).
   * - SME-SGP-Calendario-EventWorker
     - Processamento assíncrono com Celery.
   * - SME-SGP-Calendario-SyncWorker
     - Sincronização com o banco legado.
   * - SME-SGP-Calendario-ProjectionWorker
     - Atualização de projeções e consultas agregadas.

Infraestrutura de apoio: PostgreSQL, RabbitMQ, KeyDB (cache), Apache
Airflow (cargas e reconciliações) e SME-Identidade (autenticação).

Integrações
-----------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Sistema
     - Finalidade
   * - NOVO-SGP legado
     - Compatibilidade durante a migração.
   * - PAP
     - Consumo de períodos escolares.
   * - Frequência
     - Consulta de períodos e dias letivos.
   * - Planejamento
     - Consumo do calendário acadêmico.
   * - Portal Família
     - Consulta de eventos acadêmicos.
   * - Comunicados
     - Consumo de eventos do calendário.

Limites de responsabilidade
---------------------------

- O domínio é o dono exclusivo dos dados de calendário.
- Nenhum sistema externo acessa o banco diretamente: toda integração é
  por API REST ou por eventos no RabbitMQ.
- Eventos são publicados somente via Transactional Outbox.
- O comportamento funcional do legado é preservado.

Estratégia de migração
----------------------

A migração segue o padrão Strangler Fig, em fases:

#. Extração do frontend.
#. Introdução do BFF (pode ser feita depois).
#. Extração do domínio Calendário.
#. Introdução da mensageria.
#. Sincronização com o legado.
#. Substituição gradual dos consumidores.
#. Desativação do módulo legado.

Durante a coexistência, o ``SGP_DB`` continua ativo, mas a fonte oficial
do domínio é o ``SGP_CALENDARIO_DB``.

Camadas da aplicação
--------------------

Cada requisição passa pelas camadas na mesma ordem:

.. code-block:: text

   HTTP -> api/views.py -> services.py -> repository.py -> models.py

- ``apps/core``: autenticação por API Key e endpoint de health.
- ``apps/calendario``: domínio do Calendário Escolar.
