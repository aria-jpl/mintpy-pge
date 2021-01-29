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

mode=$1

# function for floating-point comparison
compare() (IFS=" "
  exec awk "BEGIN{if (!($*)) exit(1)}"
)

if [ $mode = frame ]; then
  echo "Running in frame (SNWE bounds) mode"
  north_bound=$2
  south_bound=$3
  west_bound=$4
  east_bound=$5


  if compare "${north_bound} < ${south_bound}"; then
    echo "ERROR: north bound ${north_bound} must be greater than south bound ${south_bound}"
    exit 1
  fi

  if compare "${west_bound} < ${east_bound}"; then
    echo "ERROR: west_bound bound ${west_bound} must be greater than east bound ${east_bound}"
    exit 1
  fi

  bounds="${south_bound} ${north_bound} ${west_bound} ${east_bound}"
  track_number=$6
  start_date=$7
  end_date=$8

  command_to_run="python3 ${pge_root}/run_pge.py --bounds "\"$bounds\"" --tracknumber "\"$track_number\"" --start "\"$start_date\"" --end "\"$end_date\"



elif [ $mode = region ]; then
  echo "Running in region (GeoJSON polygon) mode"
  track_number=$2
  start_date=$3
  end_date=$4

  command_to_run="python3 ${pge_root}/run_pge.py -c --tracknumber "\"$track_number\"" --start "\"$start_date\"" --end "\"$end_date\"

else
  echo "Invalid mode: $mode"
  exit 1

fi

echo "About to run: ${command_to_run}"
echo "For STDOUT and STDERR of internal processes, check out.log and err.log"
if [ $UID = 4001 ]; then
#  Running on SOAMC cluster
  conda run -n ariaMintpy /bin/bash -c "${command_to_run} > out.log 2>err.log"
else
#  Running in local dev environment
  conda run -n ariaMintpy /bin/bash -c "${command_to_run} > out.log 2>err.log"
#  conda run -n ariaMintpy /bin/bash -c "${command_to_run} > /dev/tty 2>&1"
fi