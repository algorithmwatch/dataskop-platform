#!/usr/bin/env bash

# restore from an compress but unencrypted database dump
# ./restore.sh /path/to/backup.psql.gz

docker-compose -f production.yml run --rm django bash -c "python manage.py dbrestore --uncompress --input-path $1"
