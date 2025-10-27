#! /usr/bin/env bash

set -e


container_name="opensto-db-1"
security_database=security_resources

docker exec -it $container_name psql -U postgres -d postgres -c "DROP DATABASE $security_database;"
docker exec -it $container_name psql -U postgres -d postgres -c "CREATE DATABASE $security_database;"
