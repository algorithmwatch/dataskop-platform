# `dataskop-platform`

The Data Donation Platform (DDP) of [DataSkop](https://dataskop.net/), developed by [AlgorithmWatch](https://algorithmwatch.org/).

This project was initially bootstrapped with [Django-Cookie-Cutter](https://github.com/pydanny/cookiecutter-django) but heavily modified.

## Development

### Development setup

Get the code and create .ENV files for local development.

```bash
git clone git@github.com:algorithmwatch/dataskop-platform.git
cd dataskop-platform
cp -r docs/exampleenv .envs
```

Adjust `.envs/.local` to you needs.
See [docs/exampleenv](./docs/exampleenv).

#### Git hook

For consistent code formating, we provide a [format script](./scripts/format.sh).
Since git hooks are not stored with git, you have to configure it on your local machine.

Set up a pre-commit [git hook](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks) in `.git/hooks/pre-commit` with the following content.

```bash
#!/usr/bin/env bash

# If any command fails, exit immediately with that command's exit status
set -xeo pipefail

docker-compose -f docker-compose.local.yml run --rm django ./scripts/check_format.sh
```

Ensure the file is executable: `chmod +x .git/hooks/pre-commit` and the following config is not empty: `git config core.hooksPath`.
If it's empty, set it like this:

```bash
git config core.hooksPath .git/hooks
```

#### Development with VS Code Development Container

We recommend to use [VS Code](https://code.visualstudio.com/) with the [Docker](https://docs.docker.com/get-docker/)-based [VS Code Development Container](https://code.visualstudio.com/docs/remote/containers).
As an alternative, see below on how to use Docker without VS Code.

To start the development server: Open a new terminal and see how `/start` will get executed automatically to open two dev servers (Django, Wepback).
To run management command, stop the dev servers and run `./manage.py $command`, e.g., `./manage.py makemigrations`.

If you add a new VS Code extension, you need to remove this named volume `docker volume rm dataskop_extensions`. ([See more](https://code.visualstudio.com/docs/remote/containers-advanced#_avoiding-extension-reinstalls-on-container-rebuild))

##### To get started

```bash
./manage migrate
./manage createsuperuser
./manage seeddata
/start
```

#### Development with Docker-Compose

Install and use [Docker](https://docs.docker.com/get-docker/) with Docker-Compose. ([See more](https://cookiecutter-django.readthedocs.io/en/latest/developing-locally-docker.html))

Start development setup:

```bash
./local.sh
```

To to run management commands:

```bash
./local.sh manage migrate
```

### Testing

To run the tests, check your test coverage:

```bash
coverage run -m pytest
coverage report
```

To only run tests:

```bash
pytest
```

### View sent E-Mail during development

In development, we use [MailHog](https://github.com/mailhog/MailHog) as a local SMTP server with a web interface. View sent emails at: <http://localhost:8025>

### Preview E-Mails

We are using [Django-Herald](https://github.com/worthwhile/django-herald) to send emails. To preview the generated texts, go to: <http://localhost:8000/herald/>

### Celery

To run a celery worker:

```bash
cd dataskop
celery -A config.celery_app worker -l info -Q high_priority,low_priority,celery
```

Please note: For Celery's import magic to work, it is important _where_
the celery commands are run. If you are in the same folder with
_manage.py_, you should be right.

## Production

### Settings via environment varibales

See [docs/exampleenv/.production/.django](./docs/exampleenv/.production/.django).
Also the [cookiecutter docs](http://cookiecutter-django.readthedocs.io/en/latest/settings.html) may help for some settings.

### Deployment

[Docker-Compose](./docs/deployment_docker_compose.md) (originating from Django-Cookie-Cutter)

### Sentry

Setup [Sentry](https://sentry.io) to monitor errors.
Set the `SENTRY_DSN` as environment variable.

### E-Mail service

Right now, we only support [Mailjet](https://www.mailjet.com/) but we could make any other email service from [django-anymail](https://github.com/anymail/django-anymail) work.

## License

Affero General Public License 3.0
