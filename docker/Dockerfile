FROM hysds/pge-base:latest
MAINTAINER edunn "Alexander.E.Dunn@jpl.nasa.gov"
LABEL description="Multi-Temporal Anomaly Detection for SAR Earth Observations MintPy PGE"

ARG id
ARG gid

USER ops
WORKDIR /home/ops/verdi/ops

# Set up virtual environment for ARIA-tools/MintPy
COPY ariaMintpy_env.yml ariaMintpy_env.yml
RUN echo "==========Start creating the environment and install dependencies with conda=========="
RUN /bin/bash --login -c "conda env create -f ariaMintpy_env.yml"

# Clone project dependencies
RUN set -ex \
 && echo "==========Cloning ARIA-tools==========" \
 && git clone https://github.com/aria-tools/ARIA-tools.git \
 && echo "==========Checking out the latest release for ARIA-tools==========" \
 && pushd ARIA-tools \
# && ariaPath=$(pwd) \
# && latesttag=$(git describe --tags) \
# && IFS='-' read -ra latestRelease <<< "${latesttag}" ; unset IFS \
# && echo "${latestRelease}" \
# && git checkout ${latestRelease} \
# TEMPORARY DEV VERSION CHECKOUT TO FIX NETRC
 && git checkout 35e689f53746f882065ec437cd825af729cd3e2f \
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

ENV ARIATOOLSHOME "/home/ops/verdi/ops/ARIA-tools"
ENV ARIABINS "${ARIATOOLSHOME}/tools/bin"
ENV PYTHONPATH "${PYTHONPATH}${PYTHONPATH:+:}/home/ops/verdi/ops/ARIA-tools/tools"
ENV PATH "${PATH}${PATH:+:}/home/ops/verdi/ops/binARIA-tools/tools/"
ENV PATH "${PATH}${PATH:+:}/home/ops/verdi/ops/binARIA-tools/tools/ARIAtools"

ENV MINTPYHOME "/home/ops/verdi/ops/MintPy"
ENV PYTHONPATH "${PYTHONPATH}:/home/ops/verdi/ops/MintPy/"
ENV PATH "${PATH}:/home/ops/verdi/ops/MintPy/mintpy"

# Make subsequent RUN commands use the conda environment:
# per https://pythonspeed.com/articles/activate-conda-dockerfile/
SHELL ["/opt/conda/bin/conda", "run", "-n", "ariaMintpy", "/bin/bash", "-c"]

RUN echo "==========Install third party dependencies for ARIA-tools==========" \
 && cd /home/ops/verdi/ops/ARIA-tools \
 && python3 setup.py build \
 && python3 setup.py install

# Copy in scripts and configuration
COPY wrapper_scripts wrapper_scripts
COPY smallbaselineApp.cfg smallbaselineApp.cfg
COPY run_pge.py run_pge.py
COPY run.sh run.sh

COPY .netrc /home/ops/.netrc
RUN sudo chown ops:ops /home/ops/.netrc
RUN chmod go-r /home/ops/.netrc

# set entrypoint
WORKDIR /home/ops
CMD ["/bin/bash", "--login"]