# SME-SGP-Calendario-Microsservico

Microsserviço do Calendário Escolar da Rede Municipal de Ensino. É extraído
do monólito NOVO-SGP pelo padrão Strangler Fig e passa a ser o dono dos dados
de calendário.

## Estrutura dos apps

| App | Responsabilidade | Prefixo da API |
|-----|------------------|----------------|
| `apps.core` | Autenticação por API Key e health | `/api/v1/` |
| `apps.calendario` | Domínio do Calendário Escolar | `/api/v1/calendario/` |

Dentro de cada app, a requisição segue
`api/views.py → services.py → repository.py → models.py`, e os testes ficam
em `apps/<app>/tests/`.

## Pré-requisitos

- Docker e Docker Compose
- GNU Make
- Python 3.12, para rodar o pre-commit no host

## Configuração

Copie o exemplo e preencha os valores:

```bash
cp .env.example .env
```

| Variável | Descrição |
|----------|-----------|
| `DJANGO_SECRET_KEY` | Chave secreta do Django. Sem ela, o servidor não sobe. |
| `DJANGO_DEBUG` | `1` para desenvolvimento, `0` para produção. |
| `DJANGO_ALLOWED_HOSTS` | Hosts aceitos, separados por vírgula. |
| `API_KEY` | Chave exigida nas chamadas entre serviços. |
| `API_KEY_HEADER` | Nome do header da chave (padrão `X-API-Key`). |
| `URL_BANCO_CALENDARIO` | URL do PostgreSQL: `postgresql://usuario:senha@host:porta/banco`. |
| `DB_POOL_SIZE` | Tamanho do pool de conexões. |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Banco do container de desenvolvimento. |
| `PORT_WEB`, `PORT_DEBUGPY` | Portas expostas no host em desenvolvimento. |

No `docker-compose-dev.yml`, o host do banco é `banco` e a porta é `5432`.
O `.env` nunca é commitado.

## Executar com Docker

```bash
make build
make run
make migrate
```

A API fica em `http://localhost:<PORT_WEB>/api/v1/` e o debugpy escuta em
`<PORT_DEBUGPY>`. O código é montado no container, então as alterações
recarregam sozinhas. Para parar:

```bash
make stop
```

Para testar a imagem de produção (gunicorn, usuário não-root):

```bash
docker compose up -d --build
```

### Comandos do Makefile

| Comando | O que faz |
|---------|-----------|
| `make run` | Sobe a app e o banco em segundo plano |
| `make build` | Reconstrói a imagem de desenvolvimento |
| `make stop` | Para e remove os containers |
| `make test` | Roda os testes |
| `make lint` | Roda black, ruff e mypy |
| `make coverage` | Roda os testes com cobertura mínima de 80% |
| `make schema` | Valida e gera o schema OpenAPI em `schema.yml` |
| `make docs` | Gera a documentação Sphinx em `docs/_build/html/` |
| `make migrate` | Aplica as migrations |
| `make makemigrations` | Cria migrations a partir dos models |

Todos rodam dentro do container de desenvolvimento.

## Testes e qualidade

```bash
make coverage
./scripts/executar_testes_docker.sh
```

O script faz o mesmo que `make coverage` e serve para ambientes sem `make`,
como o pipeline de CI.

O pre-commit roda black, ruff e mypy a cada commit. Instale uma vez, após
clonar:

```bash
python -m venv .venv
pip install -r requirements/local.txt
pre-commit install
```

Para verificar todos os arquivos:

```bash
./scripts/executar_precommit.sh
```

Testes E2E (Cypress, Postman) ficam em `testes/`.

## Autenticação

Os endpoints exigem uma API Key no header definido em `API_KEY_HEADER`, com o
valor de `API_KEY`. Sem a chave, ou com uma chave inválida, a resposta é
`401`.

```bash
curl -H "X-API-Key: <sua-api-key>" http://localhost:<PORT_WEB>/api/v1/<rota>
```

O health, o schema e o Swagger são públicos.

## Documentação da API

| URL | Descrição |
|-----|-----------|
| `/api/v1/docs/` | Swagger UI |
| `/api/v1/schema/` | Schema OpenAPI 3 |

## Endpoints implementados

| Método | Rota | Autenticação | Descrição |
|--------|------|--------------|-----------|
| GET | `/api/v1/health/` | Pública | Retorna `{"status": "ok"}` para liveness e readiness |

## Documentação de domínio

Regras de negócio, arquitetura e ADRs ficam em `docs/`, em Sphinx:

```bash
make docs
```

Abra `docs/_build/html/index.html` no navegador.

## Observações por sistema operacional

- **Windows:** rode os scripts `.sh` pelo Git Bash
  (`& "C:\Program Files\Git\bin\bash.exe" scripts/<script>.sh`). O comando
  `bash` do PowerShell costuma ser o do WSL.
- **Mac com Apple Silicon:** os composes fixam `linux/amd64`. Ative em
  Docker Desktop → Settings → General a opção
  *Use Rosetta for x86_64/amd64 emulation on Apple Silicon*.
