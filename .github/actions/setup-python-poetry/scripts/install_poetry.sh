#!/bin/bash

# Exit script on error
set -e

# Define a default Python version if none is provided
PYTHON_VERSION=${1:-"3.10"}

# Update system packages
echo "Updating system packages..."
sudo apt-get update

# Install the specified Python version
echo "Installing Python version $PYTHON_VERSION..."
sudo apt-get install python"${PYTHON_VERSION}"-dev python3-pip -y

# Install Poetry
echo "Installing Poetry..."
curl -sSL https://install.python-poetry.org | python3 -
echo "Poetry installed successfully."
