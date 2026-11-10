#!/usr/bin/env bash
# Roda os hooks do pre-commit (black, ruff e mypy) em todos os arquivos.
set -euo pipefail

cd "$(dirname "$0")/.."

pre-commit run --all-files
