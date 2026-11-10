# Imagem de produção: instala só requirements/base.txt e roda com gunicorn.

FROM python:3.12-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements/base.txt requirements/base.txt
RUN pip install --prefix=/install -r requirements/base.txt


FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY --from=builder /install /usr/local
COPY --chown=app:app manage.py ./
COPY --chown=app:app config ./config
COPY --chown=app:app apps ./apps

USER app

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]
