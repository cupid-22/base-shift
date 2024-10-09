#!/bin/bash

set -e

echo "Syncing and updating submodules on branch ${{ inputs.branch }}..."

# Ensure submodules are fetched
git submodule sync --recursive
git submodule update --init --recursive

# Checkout specified branch for submodules
git submodule foreach git pull origin ${{ inputs.branch }}
