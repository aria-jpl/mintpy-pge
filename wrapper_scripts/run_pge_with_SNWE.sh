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
#echo "Owning pge_root and cwd"
#sudo chown -R ops:ops $pge_root .

echo "Copying MintPy config to working directory"
cp "${pge_root}/smallbaselineApp.cfg" "./smallbaselineApp.cfg"

echo "Running PGE"
export PATH="/home/ops/.conda/envs/ariaMintpy/bin:${PATH}"
echo "Using python: $(command -v python)"
python3 ${pge_root}/run_pge.py --bounds "18.8 20.3 -156.1 -154.8" --tracknumber "124" --start "20181215" --end "20190121"