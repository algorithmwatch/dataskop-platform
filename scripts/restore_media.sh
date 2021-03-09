#!/usr/bin/env bash

# restore from compressed but unencrypted media files
# ./restore.sh /path/to/backup.psql.gz

docker-compose -f docker-compose.production.yml run --rm django bash -c "python manage.py mediarestore --uncompress --input-path $1"
