#!/bin/bash

set -ex

pip install -r requirements/build.txt

if command -v yum &> /dev/null
then
    yum update

    yum install -y \
        pkgconfig \
        boost \
        boost-thread \
        boost-devel \
        libgomp \
        hdf5-openmpi \
        lz4-devel
else
    apt-get update

    apt-get install \
        pkg-config \
        libboost-all-dev \
        libopenmpi-dev \
        libomp5 \
        libomp-dev \
        libhdf5-openmpi-dev \
        liblz4-dev
fi
