FROM ubuntu:22.04 AS base

USER root

# coloring syntax for headers
ENV CYAN='\033[0;36m'
ENV CLEAR='\033[0m'
ENV DEBIAN_FRONTEND='noninteractive'

# setup ubuntu user
ARG UID_='1000'
ARG GID_='1000'
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
    apt update && \
    apt install -y \
        software-properties-common \
        wget && \
    rm -rf /var/lib/apt/lists/*

# install blender
ARG VER=3.4.0
ENV BLENDER_VERSION=3.4
RUN echo "\n${CYAN}INSTALL BLENDER${NO_COLOR}"; \
    wget \
        https://mirror.clarkson.edu/blender/release/Blender$BLENDER_VERSION/blender-$VER-linux-x64.tar.xz \
        -O blender.tar.xz && \
    tar xf blender.tar.xz && \
    rm blender.tar.xz && \
    mv blender-$VER-linux-x64 blender && \
    chown -R ubuntu:ubuntu blender

# setup python
ARG BLENDER_PYTHON=/home/ubuntu/blender/$BLENDER_VERSION/python/bin/python3.10
RUN echo "\n${CYAN}SETUP PYTHON${NO_COLOR}"; \
    wget https://bootstrap.pypa.io/get-pip.py -O get-pip.py && \
    chown -R ubuntu:ubuntu get-pip.py && \
    $BLENDER_PYTHON get-pip.py
ENV PYTHONPATH $PYTHONPATH:/blender/$BLENDER_VERSION/python/lib/python3.10
ENV PYTHONPATH $PYTHONPATH:/blender/$BLENDER_VERSION/python/lib/python3.10/site-packages
ENV PYTHONPATH $PYTHONPATH:/home/ubuntu/blender/$BLENDER_VERSION/scripts/modules
ENV PATH /home/ubuntu/blender/$BLENDER_VERSION/python/bin:$PATH

# install shot-glass
USER ubuntu
ENV REPO='shot-glass'
RUN echo "\n${CYAN}INSTALL SHOT-GLASS{CLEAR}"; \
    $BLENDER_PYTHON install shot-glass
