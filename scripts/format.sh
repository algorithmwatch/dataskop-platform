#!/usr/bin/env bash
set -e
set -x

prettier --write .
black .
isort .
djhtml -i ./**/templates/**/*.html -t 2
