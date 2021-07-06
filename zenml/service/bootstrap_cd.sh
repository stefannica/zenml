#! /usr/bin/env bash
# script ends when one of the statements is non-zero
set -e

# make versions if it does not exist
mkdir -p alembic/versions || true

# Let the DB start
python bootstrap.py