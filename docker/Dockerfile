FROM hysds/pge-base:latest
MAINTAINER edunn "Alexander.E.Dunn@jpl.nasa.gov"
LABEL description="Multi-Temporal Anomaly Detection for SAR Earth Observations MintPy PGE"

ARG id
ARG gid

ENV verdi_root="/home/ops/verdi/ops"
ENV pge_root="${verdi_root}/mintpy-pge"
ENV work_dir="/data/mintpy-pge"

# Set up virtual environment for ARIA-tools/MintPy
WORKDIR $verdi_root
COPY ariaMintpy_env.yml ariaMintpy_env.yml
RUN echo "==========Start creating the environment and install dependencies with conda=========="
RUN /bin/bash --login -c "conda env create -f ariaMintpy_env.yml"

# Clone project dependencies
RUN set -ex \
 && echo "==========Cloning ARIA-tools==========" \
# && git clone https://github.com/aria-tools/ARIA-tools.git \
# TEMPORARY ALEX VERSION TO FIX IMPORT ISSUE \
 && git clone https://github.com/alexdunncs/ARIA-tools.git \
 && echo "==========Checking out the latest release for ARIA-tools==========" \
 && pushd ARIA-tools \
# && ariaPath=$(pwd) \
# && latesttag=$(git describe --tags) \
# && IFS='-' read -ra latestRelease <<< "${latesttag}" ; unset IFS \
# && echo "${latestRelease}" \
# && git checkout ${latestRelease} \
# TEMPORARY ALEX VERSION TO FIX IMPORT ISSUE
 && git checkout dev \
# TEMPORARY DEV VERSION CHECKOUT TO FIX NETRC
# && git checkout 35e689f53746f882065ec437cd825af729cd3e2f \
 && popd \
 && echo "==========Cloning MintPy==========" \
 && git clone https://github.com/insarlab/MintPy.git \
 && echo "==========Checking out the latest release for MintPy==========" \
 && pushd MintPy \
# && mintpyPath=$(pwd) \
 && latesttag=$(git describe --tags) \
 && IFS='-' read -ra latestRelease <<< "${latesttag}" ; unset IFS \
 && echo "${latestRelease}" \
 && git checkout ${latestRelease} \
 && popd


# Set necessary environment variables

ENV GDAL_HTTP_COOKIEFILE "/tmp/cookies.txt"
ENV GDAL_HTTP_COOKIEJAR "/tmp/cookies.txt"
ENV VSI_CACHE "YES"

ENV MINTPYHOME "${verdi_root}/MintPy"
ENV PYTHONPATH "${PYTHONPATH}:${MINTPYHOME}"
ENV PATH "${PATH}${PATH:+:}${MINTPYHOME}/mintpy"

# Make subsequent RUN commands use the conda environment:
# per https://pythonspeed.com/articles/activate-conda-dockerfile/
SHELL ["/opt/conda/bin/conda", "run", "-n", "ariaMintpy", "/bin/bash", "-c"]

ARG ARIATOOLSHOME="${verdi_root}/ARIA-tools"
RUN echo "==========Install third party dependencies for ARIA-tools==========" \
 && cd $ARIATOOLSHOME \
 && python3 setup.py build \
 && python3 setup.py install

# Copy in scripts and configuration
USER root
COPY . $pge_root
RUN set -ex \
 && sudo chown -R ops:ops $pge_root

# Create data output directory
USER root
WORKDIR $work_dir
RUN set -ex \
 && sudo chown -R ops:ops $work_dir

# set entrypoint
USER ops
WORKDIR $work_dir
CMD ["/bin/bash", "--login"]