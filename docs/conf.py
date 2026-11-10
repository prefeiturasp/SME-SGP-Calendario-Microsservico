"""Configuração do Sphinx para a documentação de domínio."""

project = "SME-SGP-Calendario-Microsservico"
copyright = "2026, SME"
author = "SME"
version = "0.1.0"
release = "0.1.0"

extensions: list[str] = []

# contexto/ guarda material de apoio em Markdown, fora do Sphinx.
exclude_patterns = ["_build", "contexto", "Thumbs.db", ".DS_Store"]

language = "pt_BR"

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
