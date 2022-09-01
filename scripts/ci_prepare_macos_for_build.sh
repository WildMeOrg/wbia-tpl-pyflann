#!/bin/bash

set -ex

brew install \
    pkg-config \
    boost \
    boost-mpi \
    open-mpi \
    libomp \
    hdf5-mpi \
    lz4
