#!/bin/bash

# Exit script on error
set -e

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
  echo "Error: Python is not installed."
  exit 1
fi

# Install Poetry
echo "Installing Poetry..."
curl -sSL https://install.python-poetry.org | python3 -
echo "Poetry installed successfully."

# Check Poetry installation
poetry --version
