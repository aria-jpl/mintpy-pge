#!/bin/bash

track_number=$1
download_dir=$2
bounding_box=$3
start=$4
end=$5
download=$6

conda_base=$(conda info --base)
source "${conda_base}/etc/profile.d/conda.sh"
conda activate ariaMintpy
ariaDownload.py -t "$track_number" -w "$download_dir" -b "$bounding_box" -s "$start" -e "$end" -o "$download"