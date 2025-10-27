#! /usr/bin/env bash

set -e


message=$1

export POSTGRES_SERVER=$(echo $(docker inspect opensto-db-1 -f ' {{.NetworkSettings.Networks.opensto_default.IPAddress}}') | tr -d '[:space:]')
alembic revision --autogenerate -m "$message"

sed -i -e '1i import sqlmodel' "$(ls -ltrh src/alembic/versions/*.py | grep -Po '[^ ]+\.py')"