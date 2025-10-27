#! /usr/bin/env bash

set -e

./scripts/pre_start.sh

uvicorn src.main:app --host 0.0.0.0 --port 80
