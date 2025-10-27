#!/bin/bash

# Make folder containing the script the root folder for its execution
cd $(dirname $0)

sudo true
sudo containerlab destroy --topo tc46b-phy.clab.yml
sudo rm -rf clab-tc46b-phy/ .tc46b-phy.clab.yml.bak
