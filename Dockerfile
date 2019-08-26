################################################################################
# Preliminary stage where OMI private projects will be installed
# This is a preliminary image in order to avoid saving sensitive information on
# the final docker image. For example, the git credentials.
FROM python:3.7-slim as intermediate

# Additional packages not included in the base image
RUN apt-get update && apt-get install -y --no-install-recommends \
    git openssh-client build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /root/.ssh/
# You need to generate these secret files, check the README
ADD conf/github /root/.ssh/id_rsa
ADD conf/github.pub /root/.ssh/id_rsa.pub
# make sure bitbucket domain is accepted
RUN touch /root/.ssh/known_hosts
RUN ssh-keyscan github.com >> /root/.ssh/known_hosts

# install all OMI requirements as wheels
RUN mkdir /tmp/wheels
WORKDIR /tmp
ADD requirements.txt .
RUN pip install --upgrade pip==19.2.3 && \
    pip wheel --wheel-dir /tmp/wheels -r requirements.txt

################################################################################
FROM python:3.7-slim

# Additional packages not included in the base image
RUN apt-get update && apt-get install -y --no-install-recommends \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies from wheels generated in intermediate image
COPY --from=intermediate /tmp/wheels /tmp/wheels
RUN pip install --upgrade pip==19.2.3 && \
    pip install /tmp/wheels/*.whl

# Copy and install iguazu
RUN mkdir /code
WORKDIR /code
COPY setup.cfg setup.py ./
COPY iguazu ./iguazu
#RUN mkdir /root/.dask
#COPY config.yaml /root/.dask/config.yaml
RUN pip install .
