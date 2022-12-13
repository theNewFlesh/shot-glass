FROM ubuntu:20.04 AS base

USER root

# coloring syntax for headers
ENV CYAN='\033[0;36m'
ENV CLEAR='\033[0m'
ENV DEBIAN_FRONTEND='noninteractive'
ENV CC=gcc
ENV CXX=g++
ENV LANG "C"
ENV LANGUAGE "C"
ENV LC_ALL "C"

# setup ubuntu user
ARG UID_='1000'
ARG GID_='1000'
RUN echo "\n${CYAN}SETUP UBUNTU USER${CLEAR}"; \
    addgroup --gid $GID_ ubuntu && \
    adduser \
        --disabled-password \
        --gecos '' \
        --uid $UID_ \
        --gid $GID_ ubuntu && \
    usermod -aG root ubuntu
WORKDIR /home/ubuntu

# update ubuntu and install basic dependencies
RUN echo "\n${CYAN}INSTALL GENERIC DEPENDENCIES${CLEAR}"; \
    apt update && \
    apt install -y \
        curl \
        git \
        graphviz \
        npm \
        pandoc \
        parallel \
        python3-pydot \
        software-properties-common \
        tree \
        vim \
        wget

# install zsh
RUN echo "\n${CYAN}SETUP ZSH${CLEAR}"; \
    apt install -y zsh && \
    curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh \
        -o install-oh-my-zsh.sh && \
    echo y | sh install-oh-my-zsh.sh && \
    mkdir -p /root/.oh-my-zsh/custom/plugins && \
    cd /root/.oh-my-zsh/custom/plugins && \
    git clone https://github.com/zdharma-continuum/fast-syntax-highlighting && \
    git clone https://github.com/zsh-users/zsh-autosuggestions && \
    npm i -g zsh-history-enquirer --unsafe-perm && \
    cd /home/ubuntu && \
    cp -r /root/.oh-my-zsh /home/ubuntu/ && \
    chown -R ubuntu:ubuntu \
        .oh-my-zsh \
        install-oh-my-zsh.sh && \
    echo 'UTC' > /etc/timezone

# install node.js, needed by jupyterlab
RUN echo "\n${CYAN}INSTALL NODE.JS${CLEAR}"; \
    curl -sL https://deb.nodesource.com/setup_16.x | bash - && \
    apt upgrade -y && \
    apt install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# install blender
ARG VER=3.2.1
ENV BLENDER_VERSION=3.2
RUN echo "\n${CYAN}INSTALL BLENDER${NO_COLOR}"; \
    wget \
        https://mirror.clarkson.edu/blender/release/Blender$BLENDER_VERSION/blender-$VER-linux-x64.tar.xz \
        -O blender.tar.xz && \
    tar xf blender.tar.xz && \
    rm blender.tar.xz && \
    mv blender-$VER-linux-x64 blender && \
    chown -R ubuntu:ubuntu blender

# setup python
ENV BLENDER_PYTHON=/home/ubuntu/blender/$BLENDER_VERSION/python/bin/python3.10
RUN echo "\n${CYAN}SETUP PYTHON${NO_COLOR}"; \
    wget https://bootstrap.pypa.io/get-pip.py -O get-pip.py && \
    chown -R ubuntu:ubuntu get-pip.py && \
    $BLENDER_PYTHON get-pip.py
ENV PYTHONPATH $PYTHONPATH:/blender/$BLENDER_VERSION/python/lib/python3.10
ENV PYTHONPATH $PYTHONPATH:/blender/$BLENDER_VERSION/python/lib/python3.10/site-packages
ENV PYTHONPATH $PYTHONPATH:/home/ubuntu/blender/$BLENDER_VERSION/scripts/modules
ENV PATH /home/ubuntu/blender/$BLENDER_VERSION/python/bin:$PATH
# ------------------------------------------------------------------------------

FROM base AS dev

USER ubuntu
WORKDIR /home/ubuntu

ENV REPO='shot-glass'
ENV REPO_ENV=True
ENV PYTHONPATH "$PYTHONPATH:/home/ubuntu/$REPO/python"

# install python dependencies
COPY ./dev_requirements.txt dev_requirements.txt
COPY ./prod_requirements.txt prod_requirements.txt
RUN echo "\n${CYAN}INSTALL PYTHON DEPENDENCIES${CLEAR}"; \
    $BLENDER_PYTHON -m pip install -r dev_requirements.txt && \
    $BLENDER_PYTHON -m pip install -r prod_requirements.txt && \
    jupyter server extension enable --py --user jupyterlab_git

COPY ./henanigans.zsh-theme .oh-my-zsh/custom/themes/henanigans.zsh-theme
COPY ./zshrc .zshrc

USER root
RUN echo "\n${CYAN}FIX PERMISSIONS${CLEAR}"; \
    chown ubuntu:ubuntu \
        .zshrc \
        dev_requirements.txt \
        prod_requirements.txt
USER ubuntu
