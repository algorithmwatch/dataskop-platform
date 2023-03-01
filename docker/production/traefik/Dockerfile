FROM traefik:2.2
RUN mkdir -p /etc/traefik/acme && touch /etc/traefik/acme/acme.json && chmod 600 /etc/traefik/acme/acme.json
COPY ./docker/production/traefik/traefik.yml /etc/traefik
# Using basic auth with traefik
# COPY ./docker/production/traefik/htpasswd /etc/traefik/htpasswd
