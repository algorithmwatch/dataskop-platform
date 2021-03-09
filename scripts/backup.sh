#!/usr/bin/env bash

# use root in order to write to volume (that's owned by root by default)
# - need to copy the gpg keyring to root user (can't easily change the directory with dbbackup)

docker-compose -f docker-compose.production.yml run -u root --rm django bash -c "cp -r /home/django/.gnupg /root/.gnupg && python manage.py dbbackup --encrypt --compress --clean && python manage.py mediabackup --encrypt --compress --clean"
