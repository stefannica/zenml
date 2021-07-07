#! /usr/bin/env bash
set -e

# make versions if it does not exist
mkdir alembic/versions && true

# Let the DB start
python bootstrap.py