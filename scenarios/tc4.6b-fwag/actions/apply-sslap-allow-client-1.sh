#!/bin/bash

set -e

# Make folder containing the script the root folder for its execution
cd $(dirname $0)

SIDECAR_HOSTNAME_PORT="127.0.0.1:7070"

# SSLA Application
RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" \
    -X POST -H "Content-Type: application/json" \
    -d @./data/ssla-apply-http-allow-client-1.json \
    http://$SIDECAR_HOSTNAME_PORT/opensto/api/v1/service/apply)

STATUS_CODE=$(echo "$RESPONSE" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
BODY=$(echo "$RESPONSE" | sed -e 's/HTTPSTATUS\:.*//')
echo "STATUS_CODE: ${STATUS_CODE}"
echo "BODY: ${BODY}"

if [ $STATUS_CODE -lt 200 ] || [ $STATUS_CODE -gt 299 ] ; then
    echo "SSLA application failed"
    exit 1
else
    echo "SSLA applied"
fi
