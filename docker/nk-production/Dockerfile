# Only for deployment /w Dokku
# Check out docker/local/django/Dockerfile for the dev Dockerfile.

FROM node:14-stretch-slim as client-builder

WORKDIR /app
COPY ./package.json ./package-lock.json /app/
RUN npm install && npm cache clean --force
COPY . /app
RUN npx browserslist@latest --update-db
RUN npm run build

# Python build stage
FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  # psycopg2 dependencies
  && apt-get install -y libpq-dev \
  # Translations dependencies
  && apt-get install -y gettext \
  # needed by django-dbbackup to dump postgres
  && apt-get install -y postgresql-client \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

RUN addgroup --system django \
    && adduser --system --ingroup django django

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip install --no-cache-dir -r /requirements/production.txt \
    && rm -rf /requirements

COPY --from=client-builder --chown=django:django /app /app

USER django

WORKDIR /app
