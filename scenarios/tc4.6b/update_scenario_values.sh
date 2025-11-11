#!/bin/bash
# Copyright 2022-2025 ETSI SDG TeraFlowSDN (TFS) (https://tfs.etsi.org/)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Demo scenario values
PUBLIC_PREFIX="192.168.100.0/24"
SERVER_IP="10.10.10.30"
SERVER_IFACE="ens3"
WEBUI_PORT="30807"
WEBSOCKET_PORT="31942"

cd ~/tfs-ctrl/across_demos/opensto/scenarios/tc4.6b
find . -type f ! -name "update_scenario_values.sh" -exec sed -i "s#10.0.2.0/24#${PUBLIC_PREFIX}#g" {} +
find . -type f ! -name "update_scenario_values.sh" -exec sed -i "s#10.0.2.2/32#${PUBLIC_PREFIX}#g" {} +
find . -type f ! -name "update_scenario_values.sh" -exec sed -i "s#10.0.2.10/32#${PUBLIC_PREFIX}#g" {} +
find . -type f ! -name "update_scenario_values.sh" -exec sed -i "s#10.0.2.25#${SERVER_IP}#g" {} +
find . -type f ! -name "update_scenario_values.sh" -exec sed -i "s#enp0s3#${SERVER_IFACE}#g" {} +
find . -type f ! -name "update_scenario_values.sh" -exec sed -i "s#30435#${WEBUI_PORT}#g" {} +
find . -type f ! -name "update_scenario_values.sh" -exec sed -i "s#30287#${WEBSOCKET_PORT}#g" {} +
