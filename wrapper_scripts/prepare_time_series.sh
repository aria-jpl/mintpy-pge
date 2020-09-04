#!/bin/bash

working_directory=$1
download_dir=$2
bounding_box=$3
minimum_overlap=$4

conda_base=$(conda info --base)
source "${conda_base}/etc/profile.d/conda.sh"
conda activate ariaMintpy
echo 'ariaTSsetup.py -f "${download_dir}/*.nc" -b "$bounding_box" --mask Download --dem Download -mo "$minimum_overlap" --workdir "$working_directory"'
ariaTSsetup.py -f "${download_dir}/*.nc" -b "$bounding_box" --mask Download --dem Download -mo "$minimum_overlap"