#!/bin/bash

conda_base=$(conda info --base)
source "${conda_base}/etc/profile.d/conda.sh"
conda activate ariaMintpy
python ../run_pge.py --bounds "18.8 20.3 -156.1 -154.8" --tracknumber "124" --start "20181215" --end "20190101"
#python ../run_pge.py --shapefile "/home/ops/something.file" --tracknumber "124" --start "20181215" --end "20190101"