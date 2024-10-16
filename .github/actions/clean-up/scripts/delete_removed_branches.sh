#!/bin/bash

# Set error handling
set -e

echo "Starting enhanced branch cleanup process..."

# Ensure we have all the remote information
git fetch --prune --all

# Get list of all local branches
local_branches=$(git branch --format="%(refname:short)")

# Get list of all remote branches
remote_branches=$(git branch -r --format="%(refname:short)")

# Get default branch name (usually main or master)
default_branch=$(git remote show origin | grep 'HEAD branch' | cut -d' ' -f5)

# Get current branch
current_branch=$(git rev-parse --abbrev-ref HEAD)

echo "Default branch: $default_branch"
echo "Current branch: $current_branch"

# Function to check if branch exists on remote
branch_exists_on_remote() {
    local branch=$1
    git ls-remote --heads origin "$branch" | grep -q "$branch"
}

# Process each local branch
echo "Checking all local branches..."
for branch in $local_branches; do
    # Skip default branch and current branch
    if [ "$branch" = "$default_branch" ] || [ "$branch" = "$current_branch" ]; then
        echo "Skipping protected branch: $branch"
        continue
    fi

    # Check if branch exists on remote
    if ! branch_exists_on_remote "$branch"; then
        echo "Branch '$branch' no longer exists on remote - deleting..."
        git branch -D "$branch" || echo "Failed to delete branch: $branch"
    fi
done

# Special handling for recently merged/deleted branches
echo "Checking for recently merged/deleted branches..."
git fetch origin --prune

# Get list of branches that have [gone] status
gone_branches=$(git branch -vv | grep ': gone]' | awk '{print $1}')

if [ -n "$gone_branches" ]; then
    echo "Found branches to delete:"
    echo "$gone_branches"

    echo "$gone_branches" | while read -r branch; do
        if [ "$branch" != "$default_branch" ] && [ "$branch" != "$current_branch" ]; then
            echo "Deleting gone branch: $branch"
            git branch -D "$branch" || echo "Failed to delete branch: $branch"
        fi
    done
else
    echo "No additional gone branches found"
fi

# Clean up refs that might be left behind
echo "Cleaning up refs..."
git for-each-ref --format="%(refname:short)" refs/heads/ | while read -r branch; do
    if [ "$branch" != "$default_branch" ] && [ "$branch" != "$current_branch" ]; then
        if ! branch_exists_on_remote "$branch"; then
            echo "Cleaning up ref for: $branch"
            git branch -D "$branch" 2>/dev/null || true
        fi
    fi
done

echo "Branch cleanup completed"

# Print remaining branches for verification
echo "Remaining branches:"
git branch -a
