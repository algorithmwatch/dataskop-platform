#!/usr/bin/env bash
set -e
set -x

prettier --write .
black .
ruff check . --fix
djhtml ./**/templates/**/*.html -t 2
