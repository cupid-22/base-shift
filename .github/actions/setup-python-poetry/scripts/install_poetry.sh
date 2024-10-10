#!/bin/bash

# Exit script on error
set -e

# Update system packages
echo "Updating system packages..."
sudo apt-get update

# Install the specified Python version
echo "Installing Python version ${1}..."
sudo apt-get install python${1}-dev python3-pip -y

# Install Poetry
echo "Installing Poetry..."
curl -sSL https://install.python-poetry.org | python3 -
echo "Poetry installed successfully."
