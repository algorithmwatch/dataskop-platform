# Goliath ![image](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg) ![image](https://img.shields.io/badge/code%20style-black-000000.svg)

The Goliath project by AlgorithmWatch.

## Information & Features

This project was bootstrapped with [Django-Cookie-Cutter](https://github.com/pydanny/cookiecutter-django).

### Settings

Check out for a description of [settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html).

### Custom Bootstrap Compilation

The generated CSS is set up with automatic Bootstrap recompilation with
variables of your choice. Bootstrap v4 is installed using npm and
customised by tweaking your variables in
`static/sass/custom_bootstrap_vars`.

You can find a list of available variables [in the Bootstrap
source](https://github.com/twbs/bootstrap/blob/v4-dev/scss/_variables.scss),
or get explanations on them in the [Bootstrap
docs](https://getbootstrap.com/docs/4.1/getting-started/theming/).

Bootstrap's javascript as well as its dependencies is concatenated into
a single file: `static/js/vendors.js`.


## Development

Install and use [Docker](https://docs.docker.com/get-docker/).

https://cookiecutter-django.readthedocs.io/en/latest/developing-locally-docker.html

```bash
./locale.sh
```

To build from scratch:

```bash
./locale.sh --build --no-cache
```

### Type checks

Running type checks with mypy:

    $ mypy goliath

### Test coverage

To run the tests, check your test coverage, and generate an HTML
coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

#### Running tests with py.test

    $ pytest

### Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS
compilation](http://cookiecutter-django.readthedocs.io/en/latest/live-reloading-and-sass-compilation.html).

### Celery

This app comes with Celery.

To run a celery worker:

```bash
cd goliath
celery -A config.celery_app worker -l info
```

Please note: For Celery's import magic to work, it is important *where*
the celery commands are run. If you are in the same folder with
*manage.py*, you should be right.

### Email Server

In development, it is often nice to be able to see emails that are being
sent from your application. For that reason local SMTP server
[MailHog](https://github.com/mailhog/MailHog) with a web interface is
available as docker container.

Container mailhog will start automatically when you will run all docker
containers. Please check [cookiecutter-django Docker
documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html)
for more details how to start all containers.

With MailHog running, to view messages that are sent by your
application, open your browser and go to `http://127.0.0.1:8025`


## Deployment

Two different environments: `staging` for previewing before finally releasing to `production`.
Useful because the email handling only works if the app is deployed somewhere.

```bash
docker-compose -f staging.yml run --rm django python manage.py migrate
```

```bash
docker-compose -f staging.yml run --rm django python manage.py createsuperuser
```

```bash
docker-compose -f staging.yml up
```

### Staging

Prodect the staging enviroment with basic auth.

```bash
htpasswd -c compose/production/traefik/htpasswd user
```

### Production

#### Sentry

Sentry is an error logging aggregator service. You can sign up for a
free account at <https://sentry.io/signup/?code=cookiecutter> or
download and host it yourself. The system is setup with reasonable
defaults, including 404 logging and integration with the WSGI
application.

You must set the DSN url in production.

https://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html


The following details how to deploy this application.

#### Heroku

See detailed [cookiecutter-django Heroku
documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-on-heroku.html).

#### Docker

See detailed [cookiecutter-django Docker
documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html).


### Systemd Service

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

```bash
systemctl enable goliath-staging
```

```bash
systemctl status goliath-staging
```

```bash
systemctl start goliath-staging
```

```bash
systemctl stop goliath-staging
```

## License

Affero General Public License 3.0
