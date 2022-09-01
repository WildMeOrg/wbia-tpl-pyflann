#!/bin/bash

pip install -r requirements/build.txt

./clean.sh
python setup.py clean

pip install -r requirements.txt

python setup.py build_ext --inplace
python setup.py develop

pip install -e .
