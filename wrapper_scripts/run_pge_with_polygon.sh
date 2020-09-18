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