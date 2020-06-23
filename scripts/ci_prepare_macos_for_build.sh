#!/bin/bash

set -ex

# See https://stackoverflow.com/a/246128/176882
export CUR_LOC="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"


# Install system dependencies
brew install lz4
brew install hdf5
brew install pkg-config


# Install Python package dependencies
python -m pip install -r requirements/build.txt
