FROM hysds/pge-base:v3.0.5
MAINTAINER edunn "Alexander.E.Dunn@jpl.nasa.gov"
LABEL description="Multi-Temporal Anomaly Detection for SAR Earth Observations MintPy PGE"

ARG id
ARG gid

ENV verdi_root="/home/ops/verdi/ops"
ENV pge_root="${verdi_root}/mintpy-pge"
ENV wrapper_scripts_home="${pge_root}/wrapper_scripts"

USER root
# Set up virtual environment for ARIA-tools/MintPy
ENV CONDA_ENVS_PATH="/opt/conda/envs/"
RUN ["chown", "ops:ops", "/opt/conda/envs"]

USER ops
COPY ariaMintpy_env.yml ariaMintpy_env.yml
RUN echo "==========Start creating the environment and install dependencies with conda=========="
RUN ["/bin/bash", "--login", "-c", "conda env create -f ariaMintpy_env.yml"]

USER ops
# Clone project dependencies
RUN set -ex \
 && cd $verdi_root \
 && echo "==========Cloning ARIA-tools==========" \
 && git clone https://github.com/aria-tools/ARIA-tools.git \
 && echo "==========Checking out the correct pinned release for ARIA-tools==========" \
 && pushd ARIA-tools \
 && git checkout "v1.1.1" \
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

ENV ARIATOOLSHOME "${verdi_root}/ARIA-tools/tools"
ENV ARIABINS "${ARIATOOLSHOME}/bin"
ENV MINTPYHOME "${verdi_root}/MintPy"
ENV PYTHONPATH "${PYTHONPATH}${PYTHONPATH:+:}${ARIATOOLSHOME}:${MINTPYHOME}"
ENV PATH "${PATH}${PATH:+:}${MINTPYHOME}/mintpy:${ARIABINS}"

# Copy in scripts and configuration
COPY --chown=ops:ops . $pge_root

# Make subsequent RUN commands use the conda environment:
# per https://pythonspeed.com/articles/activate-conda-dockerfile/
USER ops
SHELL ["/opt/conda/bin/conda", "run", "-n", "ariaMintpy", "/bin/bash", "-c"]

ENV ARIATOOLSHOME="${verdi_root}/ARIA-tools"
RUN echo "==========Install third party dependencies for ARIA-tools==========" \
RUN ["/bin/bash", "--login", "-c", "python3", "${ARIATOOLSHOME}/setup.py", "build"]
RUN ["/bin/bash", "--login", "-c", "python3", "${ARIATOOLSHOME}/setup.py", "install"]

# Comment this out for local development
USER root
RUN ["chown", "-R", "1003:1003", "/opt/conda/envs"]
RUN ["chown", "-R", "1003:1003", "/home/ops/verdi/ops/mintpy-pge/polygon.json"]

# Comment this out for deployment
#COPY --chown=ops:ops .netrc .netrc
#RUN ["chmod", "og-rw", ".netrc"]
#COPY example_context.json _context.json

USER ops
CMD ["/opt/conda/bin/conda", "run", "-n", "ariaMintpy", "/bin/bash", "--login", "-c", "${wrapper_scripts_home}/run_pge_with_SNWE.sh"]