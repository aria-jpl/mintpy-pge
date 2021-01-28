# mintpy-pge
PGE wrapper for Mintpy displacement time series.

For local development, the following steps are necessary:

 - create a conda environment from ariaMintpy_env.yml
 - Clone ARIA-tools and Mintpy repos
 - Add ARIA-tools/tools and MintPy to conda env's path
 - With the env active, run `ARIA-tools/setup.py build` and `ARIA-tools/setup.py install`
 - Comment in/out the indicated lines in the Dockerfile
 - Modify `pge_root = '/home/ops/verdi/ops/mintpy-pge'` in run_pge.py to point to your development directory
 - Create/update `~/.netrc` with valid credentials for urs.earthdata.nasa.gov
 - Add MintPy's smallBaselineApp.py to path if necessary