#! /usr/bin/env bash
set -e

# Source env variables
set -o allexport
source compose.dev.env
set +o allexport

# make versions if it does not exist
mkdir alembic/versions && true

# Let the DB start
python bootstrap.py