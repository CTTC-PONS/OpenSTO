#!/bin/bash

# Make folder containing the script the root folder for its execution
cd $(dirname $0)

sudo true
sudo containerlab destroy --topo data/tc46b-emu.clab.yml
sudo rm -rf data/clab-tc46b-emu/ data/.tc46b-emu.clab.yml.bak
