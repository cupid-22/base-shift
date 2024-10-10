#!/bin/bash

set -e

branch=$1  # Takes the branch input from the action

echo "Syncing and updating submodules on branch ${branch}..."

# Ensure submodules are fetched
git submodule sync --recursive
git submodule update --init --recursive

# Checkout the specified branch for all submodules
git submodule foreach "git pull origin ${branch}"
