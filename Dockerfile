################################################################################
# Multi-stage poetry python installation based on
# https://github.com/python-poetry/poetry/issues/1879#issuecomment-59213351

################################################################################
# Stage 1: python-base
#          Used as a base Python image with the environment variables set for
#          Python and poetry
FROM python:3.7-slim AS python-base

ENV \
    # Python-related environment variables
    PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip-related environment variables
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_VERSION="20.0.2" \
    \
    # poetry-related environment variables
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.0.5 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    \
    # paths-related environment variables
    # this is where our requirements + virtual environment will live
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
################################################################################

################################################################################
# Stage 2: builder-base
#          Used to build all dependencies. This step may need some compilation
#          tools (like build-essential), which can be quite large, but we don't
#          want to distribute an image with these temporary tools
#          In this preliminary stage, OMI private projects will be installed.
#          This is a preliminary image in order to avoid saving sensitive
#          information on the final docker image, such as the git credentials.
FROM python-base AS builder-base
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        # deps for installing poetry
        curl \
        # deps for building python deps
        git openssh-client build-essential

RUN mkdir /root/.ssh/
# You need to generate these secret files, check the README
ADD conf/github /root/.ssh/id_rsa
ADD conf/github.pub /root/.ssh/id_rsa.pub
# make sure bitbucket domain is accepted
RUN touch /root/.ssh/known_hosts
RUN ssh-keyscan github.com >> /root/.ssh/known_hosts

# Install poetry - respects $POETRY_VERSION and $POETRY_HOME
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY README.rst pyproject.toml ./

# Install all requirements, including the OMI private ones, in the poetry
# environment, but do not install iguazu (hence the --no-root)
RUN sed -i -e "s/https:\/\//ssh:\/\/git@/g" pyproject.toml && \
    poetry install --no-dev --no-root
################################################################################

#################################################################################
## Stage 3: iguazu
FROM python-base AS iguazu

# copy in our built environment
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# Add dask configuration
RUN mkdir -p /home/root/.config/dask
COPY dask-config.yaml /home/root/.config/dask/distributed.yaml

# will become mountpoint of our code
WORKDIR /code
# Copy all source code except the iguazu package, so that there is
# no rebuild for each new modification
COPY pyproject.toml README.rst ./
COPY iguazu ./iguazu

# Finally, install iguazu (which will install the iguazu command line).
# This should be fast because all dependencies are already installed
RUN pip install -q .
#################################################################################
