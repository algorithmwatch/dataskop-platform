FROM traefik:2.2
RUN mkdir -p /etc/traefik/acme \
  && touch /etc/traefik/acme/acme.json \
  && chmod 600 /etc/traefik/acme/acme.json
COPY ./compose/staging/traefik/traefik.yml /etc/traefik
COPY ./compose/staging/htpasswd /etc/traefik/htpasswd
