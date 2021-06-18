# `dataskop-platform`

The Data Donation Platform (DDP) of [DataSkop](https://dataskop.net/), developed by [AlgorithmWatch](https://algorithmwatch.org/).

This project was initially bootstrapped with [Django-Cookie-Cutter](https://github.com/pydanny/cookiecutter-django) but heavily modified.

## Development setup

Get the code, create .ENV files for local development.

```bash
git clone git@github.com:algorithmwatch/dataskop.git
cd dataskop
mkdir -p .envs/.local/.django && mkdir -p .envs/.local/.postgres
```

Adjust `.envs/.local` to you needs.
See [docs/exampleenv](./docs/exampleenv).

### VS Code Development Container

We recommend to use [VS Code](https://code.visualstudio.com/) with the [Docker](https://docs.docker.com/get-docker/)-based [VS Code Development Container](https://code.visualstudio.com/docs/remote/containers).

To start the development server: Open a new terminal and run `/start`.

To run management commands: Open a new terminal and run `./manage.py $command`, e.g., `./manage.py makemigrations`.

If you add a new VS Code extension, you need to remove this named volume `docker volume rm dataskop_extensions`. ([See more](https://code.visualstudio.com/docs/remote/containers-advanced#_avoiding-extension-reinstalls-on-container-rebuild))

As an alternative, see below on how to use Docker without VS Code.

### Docker-Compose

Install and use [Docker](https://docs.docker.com/get-docker/) with Docker-Compose. [More information.](https://cookiecutter-django.readthedocs.io/en/latest/developing-locally-docker.html)

Start development setup:

```bash
./local.sh
```

Some important Django management comands:

```bash
./local.sh manage makemigrations
./local.sh manage migrate
./local.sh manage createsuperuser
./local.sh manage reset_db
./local.sh manage shell_plus --print-sql
./local.sh manage importsupport
./local.sh manage fakedata
```

### Frontend

[Not supporting IE 11 because of Tailwind v2](https://tailwindcss.com/docs/browser-support), but IE 11 usage is [dropping fast](https://gs.statcounter.com/browser-market-share/desktop/germany/#monthly-201812-202012).

If you add a new npm dependency, delete the volume in order to recreate it.

```bash
docker-compose -f docker-compose.local.yml down
docker volume rm dataskop-platform_local_node_modules
```

#### Regarding the problems of `node_modules`

There are sometimes problems with the data volume of the `node_modules` folder.
Right now it's not clear whether this is a feature or a bug of docker volumes.
Most likely we made a mistake with our setup.
The problem arises from mapping the `node_modules` to the development container of VS Code (since we need linters etc.).
This seems to prevent installing new `node_modules`.

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
cd dataskop
celery -A config.celery_app worker -l info
```

Please note: For Celery's import magic to work, it is important _where_
the celery commands are run. If you are in the same folder with
_manage.py_, you should be right.

### Viewing sent E-Mail during development

In development, we use [MailHog](https://github.com/mailhog/MailHog) as a local SMTP server
with a web interface. View sent emails at: <http://localhost:8025>

## Production

### Settings via environment varibales

See [docs/exampleenv/.django_prod](./docs/exampleenv/.django_prod).
Also the [cookiecutter docs](http://cookiecutter-django.readthedocs.io/en/latest/settings.html) may help for some settings.

### Deployment

We currently support two different Docker-based ways to deploy dataskop:

- [Docker-Compose](./docs/deployment_docker_compose.md) (originating from Django-Cookie-Cutter)
- [Dokku](./docs/deployment_dokku.md) (_preferred_, self-hosted Heroku)

### Sentry

Setup [Sentry](https://sentry.io) to monitor errors.
Set the `SENTRY_DSN` as environment variable.

### E-Mail service

Right now, we only support [Mailjet](https://www.mailjet.com/) but we could make any other email service from [django-anymail](https://github.com/anymail/django-anymail) work.

## License

Affero General Public License 3.0
