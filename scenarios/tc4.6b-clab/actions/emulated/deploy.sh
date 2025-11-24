#!/bin/bash

# Make folder containing the script the root folder for its execution
cd $(dirname $0)

sudo true
sudo containerlab deploy --topo data/tc46b-emu.clab.yml
