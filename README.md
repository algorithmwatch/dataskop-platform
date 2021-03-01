# Goliath ![image](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg) ![image](https://img.shields.io/badge/code%20style-black-000000.svg)

The Goliath project by AlgorithmWatch.

## Information & Features

This project was bootstrapped with [Django-Cookie-Cutter](https://github.com/pydanny/cookiecutter-django).

### Settings

Check out for a description of [settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html).

## Development

Install and use [Docker](https://docs.docker.com/get-docker/). [More information.](https://cookiecutter-django.readthedocs.io/en/latest/developing-locally-docker.html)

```bash
./local.sh
```

To run Django management comannds:

```bash
./local_manage.sh makemigrations
./local_manage.sh migrate
./local_manage.sh createsuperuser
./local_manage.sh reset_db
./local_manage.sh shell_plus --print-sql
./local_manage.sh importsupport
./local_manage.sh fakedata
```

### Frontend

[Not supporting IE 11 because of Tailwind v2](https://tailwindcss.com/docs/browser-support), but IE 11 usage is [dropping fast](https://gs.statcounter.com/browser-market-share/desktop/germany/#monthly-201812-202012).

There are sometimes problems with the data volume of the `node_modules` folder.
Delete the volume in order to recreate it.

```bash
docker-compose -f local.yml down
docker volume rm goliath_local_node_modules
```

### Test coverage

To run the tests, check your test coverage, and generate an HTML
coverage report:

```bash
coverage run -m pytest
coverage html
open htmlcov/index.html
```

#### Running tests with py.test

```bash
pytest
```

### Celery

To run a celery worker:

```bash
cd goliath
celery -A config.celery_app worker -l info
```

Please note: For Celery's import magic to work, it is important _where_
the celery commands are run. If you are in the same folder with
_manage.py_, you should be right.

### Email Server

In development, it is often nice to be able to see emails that are being
sent from your application. For that reason local SMTP server
[MailHog](https://github.com/mailhog/MailHog) with a web interface is
available as docker container.

Container mailhog will start automatically when you will run all docker
containers. Please check [cookiecutter-django Docker
documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html)
for more details how to start all containers.

View emails at: `http://127.0.0.1:8025`

## Deployment

Two different environments: `staging` for previewing before finally releasing to `production`.
Useful because the email handling only works if the app is deployed somewhere.

### Sentry

Setup [Sentry](https://sentry.io) and set the `SENTRY_DSN` as environment variable.

### E-Mail Services

TODO

### Staging

Using the docker-compose of the production environment of `Django-Cookie-Cutter` for our staging invironment.
For our production, we are using Dokku.

```bash
docker-compose -f production.yml run --rm django python manage.py migrate
docker-compose -f production.yml run --rm django python manage.py createsuperuser
docker-compose -f production.yml --env-file .envs/.staging/.django up
```

Protect the staging enviroment with basic auth.

```bash
htpasswd -c compose/production/traefik/htpasswd user
```

#### Docker with systemd service

Here an example on how to deploy with Docker-Compose and systemd.

Some more details in the [cookiecutter-django Docker
documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html).

```bash
cd /etc/systemd/system
vim goliath-staging.service
```

```
[Unit]
Description=Goliath (Staging)
After=docker.service

[Service]
Restart=on-failure
RestartSec=5s

Type=oneshot
RemainAfterExit=yes
StandardOutput=file:/var/log/goli.log
StandardError=file:/var/log/goli_error.log

WorkingDirectory=/root/code/goliath/
ExecStart=/usr/bin/docker-compose -f production.yml --env-file .envs/.staging/.django up -d
ExecStop=/usr/bin/docker-compose -f production.yml down

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable goliath-staging.service
```

##### Commands

Usefull commands

```bash
systemctl enable goliath-staging
systemctl status goliath-staging
systemctl start goliath-staging
systemctl stop goliath-staging
```

##### Deployment

Create a simple deployment script:

```bash
rsync -avz . awlab2:~/code/goliath
ssh awlab2 "cd code/goliath && docker-compose -f production.yml up --detach --build django && docker-compose -f production.yml run --rm django python manage.py migrate"
```

### Production

You may as well use the Docker-compose setup from `staging`.

### Dokku

Set up a [Dokku application](http://dokku.viewdocs.io/dokku/deployment/application-deployment/), create and link a Postgres DB and a Redis instance, respectivly. Then set up all the environment variables. Finally:

```bash
git push dokku
```

#### Upgrade to a specific database version

```bash
docker pull postgres:11
dokku postgres:upgrade $dbname -I 11
```

## License

Affero General Public License 3.0
