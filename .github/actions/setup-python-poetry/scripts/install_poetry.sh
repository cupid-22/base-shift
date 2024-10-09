#!/bin/bash

set -e

# Set up Python
echo "Setting up Python version ${{ inputs.python-version }}"
python -m pip install --upgrade pip
pip install poetry

# Install docs dependencies using Poetry
poetry install --only docs --no-root
