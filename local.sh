#!/usr/bin/env bash

# If you have problems, build the container from scratch:
# docker-compose -f local.yml build --no-cache

docker-compose -f local.yml up --remove-orphans "$@"
