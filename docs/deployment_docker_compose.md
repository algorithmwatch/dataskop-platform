# Deployment with Docker-Compose

Using the docker-compose of the production environment of Django-Cookie-Cutter

```bash
docker-compose -f docker-compose.production.yml run --rm django python manage.py migrate
docker-compose -f docker-compose.production.yml run --rm django python manage.py createsuperuser
docker-compose -f docker-compose.production.yml --env-file .envs/.production/.django up
```

Protect the staging enviroment with basic auth.

```bash
htpasswd -c compose/production/traefik/htpasswd user
```

## Settings via .env files

```bash
mkdir -p .envs/.production/.django && mkdir .envs/.production/.postgres
```

## Docker with systemd service

Here an example on how to deploy with Docker-Compose and systemd.

Some more details in the [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html).

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
ExecStart=/usr/bin/docker-compose -f docker-compose.production.yml --env-file .envs/.production/.django up -d
ExecStop=/usr/bin/docker-compose -f docker-compose.production.yml down

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable goliath-staging.service
```

## Commands

Usefull commands

```bash
systemctl enable goliath-staging
systemctl status goliath-staging
systemctl start goliath-staging
systemctl stop goliath-staging
```

## Deployment Script

Create a simple deployment script:

```bash
rsync -avz . awlab2:~/code/goliath
ssh awlab2 "cd code/goliath && docker-compose -f docker-compose.production.yml up --detach --build django && docker-compose -f docker-compose.production.yml run --rm django python manage.py migrate"
```
