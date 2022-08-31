#!/bin/bash

set -ex

export CUR_LOC="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

pip install -r requirements/build.txt

brew install \
    pkg-config \
    boost \
    boost-mpi \
    open-mpi \
    libomp \
    hdf5-mpi \
    lz4

python setup.py build_ext --inplace
