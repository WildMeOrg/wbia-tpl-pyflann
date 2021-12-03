#!/bin/bash

set -ex

export CUR_LOC="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

pip install -r requirements/build.txt

if command -v yum &> /dev/null
then
    yum install -y \
        pkgconfig \
        boost \
        boost-thread \
        boost-devel \
        libgomp \
        hdf5-openmpi \
        lz4-devel
else
    apt-get install \
        pkg-config \
        libboost-all-dev \
        libopenmpi-dev \
        libomp5 \
        libomp-dev \
        libhdf5-openmpi-dev \
        liblz4-dev
fi
