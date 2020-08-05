#!/bin/bash

# Ensure conda is available
source /etc/profile
source ~/.profile
source /etc/bashrc

# Activate conda environment
conda_base=$(conda info --base)
source "${conda_base}/etc/profile.d/conda.sh"
conda activate ariaMintpy

# Run PGE
python ${pge_root}/run_pge.py --bounds "18.8 20.3 -156.1 -154.8" --tracknumber "124" --start "20181215" --end "20190101"