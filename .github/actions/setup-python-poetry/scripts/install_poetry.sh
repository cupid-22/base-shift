#!/bin/bash

# Install Python version specified
python_version=$1

sudo apt-get update
sudo apt-get install python"${python_version}"-dev python3-pip -y

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
echo "Poetry installed successfully."
