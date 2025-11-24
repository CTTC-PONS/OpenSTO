#! /usr/bin/env sh

# Make folder containing the script the root folder for its execution
cd $(dirname $0)

docker compose -f docker-compose-opensto.yml --env-file dot_envs/db.env --env-file dot_envs/security.env down -v --remove-orphans
