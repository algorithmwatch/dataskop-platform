#!/usr/bin/env bash

# To run form scratch:
# ./locale --build --no-cache

docker-compose -f local.yml up --remove-orphans $1
