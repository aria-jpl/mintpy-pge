#!/bin/bash

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

echo "Copying MintPy config to working directory"
cp "${pge_root}/smallbaselineApp.cfg" "./smallbaselineApp.cfg"

echo "Running PGE"
export PATH="/home/ops/.conda/envs/ariaMintpy/bin:${PATH}"
echo "Using python: $(command -v python)"

track_number=$1
start_date=$2
end_date=$3

command_to_run="python3 ${pge_root}/run_pge.py -c --tracknumber "\"$track_number\"" --start "\"$start_date\"" --end "\"$end_date\"
echo "About to run: ${command_to_run}"
if [ $UID = 1003 ]; then
#  Running on mamba cluster
  conda run -n ariaMintpy /bin/bash -c "${command_to_run}"
else
#  Running in local dev environment
  conda run -n ariaMintpy /bin/bash -c "${command_to_run} > /dev/tty 2>&1"
fi

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