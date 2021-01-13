#!/usr/bin/env bash

# To run form scratch:
# ./local.sh --build --no-cache

docker-compose -f local.yml up --remove-orphans "$@"
