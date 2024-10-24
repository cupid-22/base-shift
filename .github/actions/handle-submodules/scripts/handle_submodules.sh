#!/bin/bash

set -e

branch=$1  # Takes the branch input from the action

echo "Syncing and updating submodules on branch ${branch}..."

# Ensure submodules are fetched
git submodule sync --recursive
git submodule update --init --recursive

# Checkout the specified branch for all submodules and handle divergent branches
git submodule foreach "
    echo 'Entering submodule: \$name';
    git fetch origin;
    if git rev-parse --abbrev-ref HEAD | grep -q 'HEAD'; then
        echo 'In detached HEAD state, skipping pull';
    else
        git config pull.rebase false  # Default to merge
        git pull origin ${branch} || {
            echo 'Conflict detected, attempting to resolve with --ff-only';
            git pull --ff-only origin ${branch};
        }
    fi
"

echo "Submodules updated successfully."
