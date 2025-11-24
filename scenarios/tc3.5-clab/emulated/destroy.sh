#!/bin/bash

# Make folder containing the script the root folder for its execution
cd $(dirname $0)

sudo true
sudo containerlab destroy --topo data/tc3.5-emu.clab.yml
sudo rm -rf data/clab-tc3.5-emu/ data/.tc3.5-emu.clab.yml.bak
