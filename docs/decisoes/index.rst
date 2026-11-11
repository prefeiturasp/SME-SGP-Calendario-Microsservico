Decisões de arquitetura
=======================

Resumo das decisões de arquitetura (ADRs) do domínio Calendário.

.. list-table::
   :header-rows: 1
   :widths: auto

   * - ADR
     - Status
     - Decisão
   * - ADR-001
     - Proposta
     - Um único microsserviço para calendários anuais e semestrais.
   * - ADR-002
     - Proposta
     - Policy Pattern para as regras de cada categoria de calendário,
       em vez de condicionais ou herança.
   * - ADR-003
     - Proposta
     - Banco PostgreSQL exclusivo do domínio (``SGP_CALENDARIO_DB``).
   * - ADR-004
     - Proposta
     - Migração gradual pelo padrão Strangler Fig.
   * - ADR-005
     - Proposta
     - Transactional Outbox: o evento é gravado na mesma transação dos
       dados e publicado no RabbitMQ por um processo Celery.
   * - ADR-006
     - Proposta
     - Inbox Pattern no consumo de eventos. Em conflito com a visão
       arquitetural, que não adota Inbox na primeira versão.
   * - ADR-007
     - Proposta
     - Microfrontend independente para a interface do Calendário.
   * - ADR-008
     - Aceita
     - Compatibilidade gradual com o legado; ``SGP_CALENDARIO_DB`` é a
       fonte oficial dos dados.
   * - ADR-009
     - Proposta
     - Não adotar CQRS na primeira versão; usar read models e
       projection workers.
