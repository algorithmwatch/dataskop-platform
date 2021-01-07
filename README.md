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

to migrate:

```bash
docker-compose -f local.yml run --rm django python manage.py migrate
```

to create a super user:

```bash
docker-compose -f local.yml run --rm django python manage.py createsuperuser
```

### Frontend

[Not supporting IE 11 because of Tailwind v2](https://tailwindcss.com/docs/browser-support), but IE 11 usage is [dropping fast](https://gs.statcounter.com/browser-market-share/desktop/germany/#monthly-201812-202012).

When adapting the `package.json` I had problems with the Docker container. Removing the volume `/app/node_modules` building the image, then adding the volume, then building again fixed this. (`docker-compose -f local.yml build node`)

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

```bash
docker-compose -f staging.yml run --rm django python manage.py migrate
docker-compose -f staging.yml run --rm django python manage.py createsuperuser
docker-compose -f staging.yml up
```

Protect the staging enviroment with basic auth.

```bash
htpasswd -c compose/production/traefik/htpasswd user
```

#### Docker with systemd service

Here an example on how to deploy with Docker-Compose and systemd.

Some more details in the [cookiecutter-django Docker
documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html).

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
ExecStart=/usr/bin/docker-compose -f staging.yml up -d
ExecStop=/usr/bin/docker-compose -f staging.yml down

[Install]
WantedBy=multi-user.target
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
ssh awlab2 "cd code/goliath && docker-compose -f staging.yml up --detach --build django && docker-compose -f staging.yml run --rm django python manage.py migrate"
```

### Production

You as well use the Docker-compose setup from `staging`.

### Heroku

Check out the [cookiecutter-django Heroku
documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-on-heroku.html).

### Dokku

Set up a [Dokku application](http://dokku.viewdocs.io/dokku/deployment/application-deployment/), create and link a Postgres DB and a Redis instance, respectivly. Then set up all the environment variables. Finally:

```bash
git push dokku
```

## License

Affero General Public License 3.0
