#!/bin/bash


conda_base=$(conda info --base)
source "${conda_base}/etc/profile.d/conda.sh"
conda activate ariaMintpy
python ../run_pge.py