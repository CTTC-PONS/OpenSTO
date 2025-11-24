#! /usr/bin/env sh

# Make folder containing the script the root folder for its execution
cd $(dirname $0)

docker compose -f docker-compose-pipeline.yml up --build -d
