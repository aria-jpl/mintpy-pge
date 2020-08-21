#!/bin/bash

download_dir=$1
bounding_box=$2
minimum_overlap=$3

conda_base=$(conda info --base)
source "${conda_base}/etc/profile.d/conda.sh"
conda activate ariaMintpy
echo 'ariaTSsetup.py -f "${download_dir}/*.nc" -b "$bounding_box" --mask Download --dem Download -mo "$minimum_overlap"'
ariaTSsetup.py -f "${download_dir}/*.nc" -b "$bounding_box" --mask Download --dem Download -mo "$minimum_overlap"