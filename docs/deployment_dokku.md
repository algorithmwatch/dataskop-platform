# Deployment with Dokku

Deployment with https://dokku.com/

## Configuration

We are using a custom nginx.conf.sigil. When updating Dokku, make sure to check if the most recent default nginx base is used.

- https://dokku.com/docs/configuration/nginx/

## Setup

Set up a [Dokku application](http://dokku.viewdocs.io/dokku/deployment/application-deployment/), create and link a Postgres DB and a Redis instance, respectivly.
Then set up all the environment variables. Finally:

```bash
git push dokku
```

### Upgrade to a specific database version

```bash
docker pull postgres:11
dokku postgres:upgrade $dbname -I 11
```

### Misc

- setup a default server: https://dokku.com/docs/configuration/nginx/#default-site
- to make the custom CHECKS file work: set a list of allowed hosts (e.g. a local IP adress): `DJANGO_ALLOWED_HOSTS=.unding.de,xx.xx.xx.xx`

### Volumes

`mkdir /var/lib/dokku/data/storage/some-storage`

The uid and gid of the user of the Dockerfile (in this case the user `django`)

`chown -R 101:101 /var/lib/dokku/data/storage/some-storage`

### Backup cronjobs

```
16 * * * * /usr/bin/dokku run unding ./manage.py dbbackup --encrypt --compress --clean
16 12,19 * * * /usr/bin/dokku run unding ./manage.py mediabackup --encrypt --compress --clean
```
