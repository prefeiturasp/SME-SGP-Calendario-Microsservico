"""Ponto de entrada WSGI do SME-SGP-Calendario-Microsservico.

Usado pelo gunicorn em produção e pelo ``runserver`` em desenvolvimento.
"""

import os

from django.core.exceptions import ImproperlyConfigured
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Falha visivelmente na subida quando a chave não está configurada
if not os.environ.get("DJANGO_SECRET_KEY"):
    raise ImproperlyConfigured("DJANGO_SECRET_KEY não configurada.")

application = get_wsgi_application()
