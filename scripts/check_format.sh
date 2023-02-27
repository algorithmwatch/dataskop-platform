#!/usr/bin/env bash
set -e
set -x

prettier --check .
black . --check
ruff check .
djhtml ./**/templates/**/*.html -t 2 --check
