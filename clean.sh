#!/bin/bash

rm -rf __pycache__
rm -rf _skbuild
rm -rf pyflann/lib
rm -rf dist
rm -rf build
rm -rf cmake-builds
rm -rf htmlcov
rm -rf pip-wheel-metadata
rm -rf *.egg-info

rm -rf index.dat
rm -rf test*.flann

rm -rf mb_work
rm -rf wheelhouse

CLEAN_PYTHON='find . -iname __pycache__ -delete && find . -iname *.pyc -delete && find . -iname *.pyo -delete'
bash -c "$CLEAN_PYTHON"
