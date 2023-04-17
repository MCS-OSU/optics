#!/bin/bash

CONDA_PATH=$(conda info | grep -i 'base environment' | cut -d ":" -f2 | cut -d " " -f2)
source $CONDA_PATH/etc/profile.d/conda.sh
