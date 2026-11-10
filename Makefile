COMPOSE = docker compose -f docker-compose-dev.yml
RUN = $(COMPOSE) run --rm calendario

.PHONY: help run build stop test lint coverage schema docs migrate \
	makemigrations

help:
	@echo Alvos disponiveis:
	@echo   make run             sobe a app e o banco em segundo plano
	@echo   make build           reconstroi a imagem de desenvolvimento
	@echo   make stop            para e remove os containers
	@echo   make test            roda os testes
	@echo   make lint            roda black, ruff e mypy
	@echo   make coverage        roda os testes com cobertura minima de 80
	@echo   make schema          valida e gera o schema OpenAPI em schema.yml
	@echo   make docs            gera a documentacao em docs/_build/html
	@echo   make migrate         aplica as migrations no banco
	@echo   make makemigrations  cria migrations a partir dos models

run:
	$(COMPOSE) up -d

build:
	$(COMPOSE) build

stop:
	$(COMPOSE) down

test:
	$(RUN) python manage.py test

lint:
	$(RUN) sh -c "black --check . && ruff check . && mypy"

coverage:
	$(RUN) sh -c "coverage run manage.py test && coverage report"

schema:
	$(RUN) python manage.py spectacular --validate --fail-on-warn \
		--file schema.yml

docs:
	$(RUN) sphinx-build -W -b html docs docs/_build/html

migrate:
	$(RUN) python manage.py migrate

makemigrations:
	$(RUN) python manage.py makemigrations
