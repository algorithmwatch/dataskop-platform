# Goliath ![image](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg) ![image](https://img.shields.io/badge/code%20style-black-000000.svg)

The Goliath project by [AlgorithmWatch](https://algorithmwatch.org/) powering [Unding.de](//unding.de).

This project was bootstrapped with [Django-Cookie-Cutter](https://github.com/pydanny/cookiecutter-django) but heavily modified.

## Development Setup

Get the code, remove devlopment .env-files from git tracking.

```bash
git clone git@github.com:algorithmwatch/goliath.git
cd goliath
git rm -r --cached --ignore-unmatch .envs/.local
```

Adjust `.envs/.local` to you needs.
See [./docs/settings.md](./docs/settings.md).

### VS Code Dev Container

We recommend to use [VS Code](https://code.visualstudio.com/) with the [Docker](https://docs.docker.com/get-docker/)-based [VS Code Development Container](https://code.visualstudio.com/docs/remote/containers).

To start the devlopment server: Open a new terminal and run `/start`.

To run management commands: Open a new terminal and run `./manage.py $command`, e.g., `./manage.py makemigrations`.

If you add a new VS Code extension, you may have to remove the named volume `docker volume rm goliath_extensions`. ([Background](https://code.visualstudio.com/docs/remote/containers-advanced#_avoiding-extension-reinstalls-on-container-rebuild))

As an alternative, see below to use Docker without VS Code.

### Docker-Compose

Install and use [Docker](https://docs.docker.com/get-docker/) with Docker-Compose. [More information.](https://cookiecutter-django.readthedocs.io/en/latest/developing-locally-docker.html)

```bash
./local.sh
```

Some important Django management comands:

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

View sent emails at: <http://localhost:8025>

## Production

### Settings via Environment Varibales

Check [docs/settings.md](./docs/settings.md) for more.
Also the [cookiecutter docs](<(http://cookiecutter-django.readthedocs.io/en/latest/settings.html)>) may help for some settings.

### Deployment

We currently support two different Docker-based ways to deploy Goliath:

- [Docker-Compose](./docs/deployment_docker_compose.md) (originating from Django-Cookie-Cutter)
- [Dokku](./docs/deployment_dokku.md) (_preferred_, self-hosted Heroku)

### Sentry

Setup [Sentry](https://sentry.io) to monitor errors.
Set the `SENTRY_DSN` as environment variable.

### E-Mail Services

See [docs/emails_mailjet.md](./docs/emails_mailjet.md) on how to configure [Mailjet](https://www.mailjet.com/).
Right now, we only support Mailjet but we could make any other email service from [django-anymail](https://github.com/anymail/django-anymail) work.

### Staging

In order to test the email receiving, you need to have Goliath deployed somewhere.
So think about creating a seperate `staging` server to test Goliath.
You take all the production settings but customize Goliath via .env files.

## License

Affero General Public License 3.0
