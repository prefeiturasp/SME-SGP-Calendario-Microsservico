"""Configurações Django do SME-SGP-Calendario-Microsservico.

Todo valor que muda entre ambientes vem de variáveis de ambiente.
As variáveis suportadas estão documentadas no ``.env.example``.
"""

import os
import sys
import urllib.parse
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent


def _ler_booleano(nome: str, padrao: str = "0") -> bool:
    """Lê uma variável de ambiente booleana.

    Args:
        nome: Nome da variável de ambiente.
        padrao: Valor usado quando a variável não está definida.

    Returns:
        True se o valor for ``1`` ou ``true`` (sem diferenciar
        maiúsculas), False caso contrário.
    """
    return os.environ.get(nome, padrao).strip().lower() in ("1", "true")


# Segurança. Sem DJANGO_SECRET_KEY o servidor não sobe: ver
# config/wsgi.py.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
DEBUG = _ler_booleano("DJANGO_DEBUG")
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
    if host.strip()
]

# Autenticação entre serviços.
API_KEY = os.environ.get("API_KEY", "")
API_KEY_HEADER = os.environ.get("API_KEY_HEADER", "X-API-Key")

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "apps.core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Banco de dados.
_DB_POOL_SIZE = int(os.environ.get("DB_POOL_SIZE", "5"))
_POOL_OPTIONS: dict[str, Any] = {
    "POOL_SIZE": _DB_POOL_SIZE,
    "MAX_OVERFLOW": 0,
    "POOL_TIMEOUT": 30,
    "POOL_RECYCLE": 1800,
    "PRE_PING": True,
}


def _url_para_bd(url: str) -> dict[str, Any]:
    """Converte a URL do banco do Calendário em configuração Django.

    Args:
        url: URL PostgreSQL no formato
            ``postgresql://usuario:senha@host:porta/nome_banco``.

    Returns:
        Dicionário de configuração do Django com pool de conexões via
        ``dj_db_conn_pool``. Sem URL, retorna SQLite em memória.
    """
    if not url:
        return {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}

    partes = urllib.parse.urlparse(url)
    return {
        "ENGINE": "dj_db_conn_pool.backends.postgresql",
        "NAME": partes.path.lstrip("/"),
        "USER": urllib.parse.unquote(partes.username or ""),
        "PASSWORD": urllib.parse.unquote(partes.password or ""),
        "HOST": partes.hostname or "",
        "PORT": str(partes.port or ""),
        "POOL_OPTIONS": _POOL_OPTIONS,
    }


DATABASES = {
    "default": _url_para_bd(os.environ.get("URL_BANCO_CALENDARIO", "")),
}

# SQLite em memória durante os testes.
if "test" in sys.argv or _ler_booleano("USE_SQLITE_TEST"):
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.core.authentication.AutenticacaoApiKey",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "SME-SGP-Calendario-Microsservico API",
    "DESCRIPTION": "API do Calendário Escolar do SGP.",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "ApiKey": {
                "type": "apiKey",
                "in": "header",
                "name": API_KEY_HEADER,
            },
        },
    },
    "SECURITY": [{"ApiKey": []}],
}
