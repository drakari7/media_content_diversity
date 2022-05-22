#!/usr/bin/env bash

# cd to directory where script is residing
cd $(dirname "$(readlink -f "$0")")

# Making sure some directories exist to avoid errors
mkdir -p cache/

source thesis_env/bin/activate
python pipeline.py

# Remove pre generated graphs so that new graphs use new data
rm -f ./static/graphs/metadata/*
rm -f ./static/graphs/tf_idf/*
