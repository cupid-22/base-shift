#!/bin/bash

# Exit script on error
set -e

# Split the input into an array of Python versions (comma-separated)
IFS=',' read -r -a PYTHON_VERSIONS <<< "${1:-"3.10,3.12,3.11"}"

# Iterate through each Python version and attempt to install it
for PYTHON_VERSION in "${PYTHON_VERSIONS[@]}"; do
  echo "Installing Python version $PYTHON_VERSION..."
    sudo apt-get update
    # Check if the version is already installed
    if command -v python"$PYTHON_VERSION" &> /dev/null; then
        echo "Python $PYTHON_VERSION is already installed. Skipping..."
    else
        sudo apt-get install -y python"${PYTHON_VERSION}"-dev python3-pip
        echo "Python $PYTHON_VERSION installed successfully."
    fi

    # Set the installed version as default
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python"${PYTHON_VERSION}" 1
done

# Check installed versions
echo "Installed Python versions:"
python3 --version
