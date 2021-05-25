#!/usr/bin/env bash

# ./local.sh

# ./local.sh manage makemigrations

# If you have problems, build the container from scratch:
# ./local.sh build

# build without cache
# ./local.sh nocache

if [ "$1" == "manage" ]; then
    shift
    docker-compose -f docker-compose.local.yml run --rm django python manage.py "$@"
    exit 0
fi

if [ "$1" == "build" ]; then
    docker-compose -f docker-compose.local.yml build
    exit 0
fi

if [ "$1" == "nocache" ]; then
    docker-compose -f docker-compose.local.yml build --no-cache
    exit 0
fi

docker-compose -f docker-compose.local.yml up --remove-orphans "$@"
