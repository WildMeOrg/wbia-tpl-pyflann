#!/bin/bash

set -ex

pip install -r requirements/build.txt

brew update

brew install \
    pkg-config \
    boost \
    boost-mpi \
    open-mpi \
    libomp \
    hdf5-mpi \
    lz4
