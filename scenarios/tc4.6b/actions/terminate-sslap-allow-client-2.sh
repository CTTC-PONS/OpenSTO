#!/bin/bash

set -e

# Make folder containing the script the root folder for its execution
cd $(dirname $0)

SIDECAR_HOSTNAME_PORT="127.0.0.1:7070"
SERVICE_ID="b78aacc6-5fd9-4ebb-a613-851fde059137"

# SSLA Termination
RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" \
    -X DELETE -H "Content-Type: application/json" \
    http://$SIDECAR_HOSTNAME_PORT/opensto/api/v1/service/apply/$SERVICE_ID)

STATUS_CODE=$(echo "$RESPONSE" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
BODY=$(echo "$RESPONSE" | sed -e 's/HTTPSTATUS\:.*//')
echo "STATUS_CODE: ${STATUS_CODE}"
echo "BODY: ${BODY}"

if [ $STATUS_CODE -lt 200 ] || [ $STATUS_CODE -gt 299 ] ; then
    echo "SSLA termination failed"
    exit 1
else
    echo "SSLA terminated"
fi
