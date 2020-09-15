#!/bin/bash

echo "Running PGE wrapper script as $(echo whoami)"
#echo "/opt/conda/envs/ariaMintpy owned by $(ls -l /opt/conda/envs/ariaMintpy)"

echo "Ensuring conda is available..."
. /opt/conda/etc/profile.d/conda.sh
conda activate base
export LD_LIBRARY_PATH=/opt/conda/lib:/usr/lib:/usr/lib64:/usr/local/lib:$LD_LIBRARY_PATH

echo "Listing available environments:"
conda env list

echo "Activating conda environment"
conda activate ariaMintpy

echo "Checking active conda environment: '${CONDA_DEFAULT_ENV}'"
echo "Checking PYTHONPATH: ${PYTHONPATH}"
#echo "Owning pge_root and cwd"
#sudo chown -R ops:ops $pge_root .

echo "Copying MintPy config to working directory"
cp "${pge_root}/smallbaselineApp.cfg" "./smallbaselineApp.cfg"

echo "Running PGE"
export PATH="/home/ops/.conda/envs/ariaMintpy/bin:${PATH}"
echo "Using python: $(command -v python)"

north_bound=$1
south_bound=$2
west_bound=$3
east_bound=$4

export bounds="${south_bound} ${north_bound} ${west_bound} ${east_bound}"
export track_number=$5
export start_date=$6
export end_date=$7

export command_to_run='python3 ${pge_root}/run_pge.py --bounds "${bounds}" --tracknumber "${track_number}" --start "${start_date}" --end "${end_date}"'
echo "About to run: ${command_to_run}"

# Comment out for deployment
#conda run -n ariaMintpy /bin/bash -c "${command_to_run} > /dev/tty 2>&1"

# Comment out for development
conda run -n ariaMintpy /bin/bash -c "${command_to_run}"

# generate dataset ID
timestamp=$(date -u +%Y%m%dT%H%M%S.%NZ)
hash=$(echo $timestamp | sha224sum | cut -c1-5)
id=multi_temporal_anomaly_detection-${timestamp}-${hash}
echo "dataset ID: $id"

mkdir $id
cp timeseries.h5 velocity.h5 waterMask.h5 $id

# create minimal dataset JSON file
dataset_json_file=${id}/${id}.dataset.json
echo "{\"version\": \"v1.0\"}" > $dataset_json_file

# create minimal metadata file
metadata_json_file=${id}/${id}.met.json
echo "{}" > $metadata_json_file