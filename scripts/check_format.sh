#!/usr/bin/env bash
set -e
set -x

prettier --check .
black . --check
isort dataskop/**/*.py --check-only
djhtml ./**/templates/**/*.html -t 2 --check
