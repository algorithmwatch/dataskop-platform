## Deployment



```bash
htpasswd -c compose/production/traefik/htpasswd user
```


https://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html


Goliath
=======

The Goliath project by AlgorithmWatch

![image](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg%0A%20%20:target:%20https://github.com/pydanny/cookiecutter-django/%0A%20%20:alt:%20Built%20with%20Cookiecutter%20Django)

![image](https://img.shields.io/badge/code%20style-black-000000.svg%0A%20%20:target:%20https://github.com/ambv/black%0A%20%20:alt:%20Black%20code%20style)

License
:   GPLv3

Settings
--------

Moved to
[settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html).

Basic Commands
--------------

### Setting Up Your Users

-   To create a **normal user account**, just go to Sign Up and fill out
    the form. Once you submit it, you'll see a "Verify Your E-mail
    Address" page. Go to your console to see a simulated email
    verification message. Copy the link into your browser. Now the
    user's email should be verified and ready to go.
-   To create an **superuser account**, use this command:

        $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and
your superuser logged in on Firefox (or similar), so that you can see
how the site behaves for both kinds of users.

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

``` {.sourceCode .bash}
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

### Sentry

Sentry is an error logging aggregator service. You can sign up for a
free account at <https://sentry.io/signup/?code=cookiecutter> or
download and host it yourself. The system is setup with reasonable
defaults, including 404 logging and integration with the WSGI
application.

You must set the DSN url in production.

Deployment
----------

The following details how to deploy this application.

### Heroku

See detailed [cookiecutter-django Heroku
documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-on-heroku.html).

### Docker

See detailed [cookiecutter-django Docker
documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html).

Custom Bootstrap Compilation \^\^\^\^\^\^

The generated CSS is set up with automatic Bootstrap recompilation with
variables of your choice. Bootstrap v4 is installed using npm and
customised by tweaking your variables in
`static/sass/custom_bootstrap_vars`.

You can find a list of available variables [in the bootstrap
source](https://github.com/twbs/bootstrap/blob/v4-dev/scss/_variables.scss),
or get explanations on them in the [Bootstrap
docs](https://getbootstrap.com/docs/4.1/getting-started/theming/).

Bootstrap's javascript as well as its dependencies is concatenated into
a single file: `static/js/vendors.js`.


## License

Affero General Public License 3.0
