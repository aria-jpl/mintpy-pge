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

export latlongbounds="18.8 20.3 -156.1 -154.8"
export command_to_run='python3 ${pge_root}/run_pge.py --bounds "${latlongbounds}" --tracknumber "124" --start "20181215" --end "20190121"'
echo "About to run: ${command_to_run}"
#conda run -n ariaMintpy /bin/bash -c "${command_to_run} > /dev/tty 2>&1"
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


#python3 ${pge_root}/run_pge.py --bounds "18.8 20.3 -156.1 -154.8" --tracknumber "124" --start "20181215" --end "20190121"