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
