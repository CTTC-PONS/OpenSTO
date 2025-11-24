#!/bin/bash

cd $(dirname $0)

docker buildx build -t traffic-sniffer:dev  -f ./traffic_sniffer/Dockerfile  .
docker buildx build -t ai-inference:dev     -f ./ai_inference/Dockerfile     .
docker buildx build -t attack-detector:dev  -f ./attack_detector/Dockerfile  .
docker buildx build -t attack-mitigator:dev -f ./attack_mitigator/Dockerfile .
docker buildx build -t topic-monitor:dev    -f ./topic_monitor/Dockerfile    .
