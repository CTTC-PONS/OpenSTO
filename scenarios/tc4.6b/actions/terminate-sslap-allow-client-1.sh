#!/bin/bash

set -e

# Make folder containing the script the root folder for its execution
cd $(dirname $0)

SIDECAR_HOSTNAME_PORT="127.0.0.1:7070"
SERVICE_ID="df320b66-52b4-4b29-b98f-0f07adab4d1b"

# Service termination
response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
    -X DELETE -H "Content-Type: application/json" \
    http://$SIDECAR_HOSTNAME_PORT/opensto/api/v1/service/apply/$SERVICE_ID)

body=$(echo "$response" | sed -e 's/HTTPSTATUS\:.*//')
status_code=$(echo "$response" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
if [ $status_code -lt 200 ] || [ $status_code -gt 299 ] ; then
    echo "Service termination failed"
    exit 1
fi

echo "Security service terminated"
