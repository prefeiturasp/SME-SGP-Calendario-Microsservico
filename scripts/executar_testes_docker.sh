#!/usr/bin/env bash
# Roda os testes com cobertura dentro do container de desenvolvimento.
set -euo pipefail

cd "$(dirname "$0")/.."

docker compose -f docker-compose-dev.yml build calendario
docker compose -f docker-compose-dev.yml run --rm calendario \
    sh -c "coverage run manage.py test && coverage report"
