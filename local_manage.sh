#!/usr/bin/env bash

docker-compose -f docker-compose.local.yml run --rm django python manage.py "$@"
