#!/usr/bin/env bash

export PYTHONWARNINGS='error::UserWarning'
python -m pdoc --force --html spixel --config sort_identifiers=False
