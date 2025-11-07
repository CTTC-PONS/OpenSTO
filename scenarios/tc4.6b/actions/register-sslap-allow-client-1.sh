#!/bin/bash

set -e

# Make folder containing the script the root folder for its execution
cd $(dirname $0)

SIDECAR_HOSTNAME_PORT="127.0.0.1:7070"

# SSLA registration
response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
    -X POST -H "Content-Type: application/json" \
    -d @./data/essla-http-allow-client-1.json \
    http://$SIDECAR_HOSTNAME_PORT/opensto/api/v1/ssla/essla)

body=$(echo "$response" | sed -e 's/HTTPSTATUS\:.*//')
status_code=$(echo "$response" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
if [ $status_code -lt 200 ] || [ $status_code -gt 299 ] ; then
    echo "SSLA registration failed"
    exit 1
fi

echo "SSLA registered"
