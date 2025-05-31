FROM ubuntu:22.04 AS base

USER root

# coloring syntax for headers
ENV CYAN='\033[0;36m'
ENV CLEAR='\033[0m'
ENV DEBIAN_FRONTEND="noninteractive"

# setup ubuntu user
ARG UID_="1000"
ARG GID_="1000"
RUN echo "\n${CYAN}SETUP UBUNTU USER${CLEAR}"; \
    addgroup --gid $GID_ ubuntu && \
    adduser \
        --disabled-password \
        --gecos '' \
        --uid $UID_ \
        --gid $GID_ ubuntu
WORKDIR /home/ubuntu

# update ubuntu and install basic dependencies
RUN echo "\n${CYAN}INSTALL GENERIC DEPENDENCIES${CLEAR}"; \
    apt update --fix-missing && \
    apt install -y \
        curl \
        software-properties-common && \
    rm -rf /var/lib/apt/lists/*

# install blender
ARG VER=3.4.0
ENV BLENDER_VERSION=3.4
RUN echo "\n${CYAN}INSTALL BLENDER${NO_COLOR}"; \
    curl -fsSL \
        https://mirror.clarkson.edu/blender/release/Blender$BLENDER_VERSION/blender-$VER-linux-x64.tar.xz \
        -o blender.tar.xz && \
    tar xf blender.tar.xz && \
    rm blender.tar.xz && \
    mv blender-$VER-linux-x64 blender && \
    chown -R ubuntu:ubuntu blender

# setup python
ARG BLENDER_PYTHON=/home/ubuntu/blender/$BLENDER_VERSION/python/bin/python3.10
RUN echo "\n${CYAN}SETUP PYTHON${NO_COLOR}"; \
    curl -fsSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    chown -R ubuntu:ubuntu get-pip.py && \
    $BLENDER_PYTHON get-pip.py
ENV PYTHONPATH $PYTHONPATH:/blender/$BLENDER_VERSION/python/lib/python3.10
ENV PYTHONPATH $PYTHONPATH:/blender/$BLENDER_VERSION/python/lib/python3.10/site-packages
ENV PYTHONPATH $PYTHONPATH:/home/ubuntu/blender/$BLENDER_VERSION/scripts/modules
ENV PATH /home/ubuntu/blender/$BLENDER_VERSION/python/bin:$PATH

# install python3.10 and pip
RUN echo "\n${CYAN}SETUP PYTHON3.10${CLEAR}"; \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt update && \
    apt install --fix-missing -y \
        python3.10-dev \
        python3.10-venv && \
    rm -rf /var/lib/apt/lists/*

# install pip
RUN echo "\n${CYAN}INSTALL PIP${CLEAR}"; \
    curl -fsSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.10 get-pip.py && \
    pip3.10 install --upgrade pip && \
    rm -rf get-pip.py

# install pdm
USER ubuntu
ENV PATH="$PATH:/home/ubuntu/.local/bin"
RUN echo "\n${CYAN}INSTALL PDM${CLEAR}"; \
    curl -sSL \
    https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py \
    | python3.10 - && \
    pip3.10 install --upgrade --user pdm && \
    pdm self update --pip-args='--user'

# setup pdm environment
RUN echo "\n${CYAN}SETUP PDM${CLEAR}"; \
    mkdir /home/ubuntu/pdm && \
    cd /home/ubuntu/pdm && \
    pdm init --python 3.10 --non-interactive && \
    rm -rf src tests README.md __pycache__ .gitignore && \
    pdm venv create -n prod-3.10;

# install shot-glass
USER ubuntu
COPY --chown=ubuntu:ubuntu config/prod.toml /home/ubuntu/pdm/pyproject.toml
ARG VERSION
RUN echo "\n${CYAN}INSTALL SHOT-GLASS${CLEAR}"; \
    cd /home/ubuntu/pdm && \
    pdm add -v "shot-glass==$VERSION";

ENV PATH="/home/ubuntu/pdm/.venv/bin:$PATH"
