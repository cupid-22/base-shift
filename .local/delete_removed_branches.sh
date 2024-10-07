#!/bin/bash

# Function to delete branches that no longer exist on the remote
delete_removed_branches() {
  local repo_path=$1
  cd "$repo_path" || exit

  echo "Fetching and pruning remote branches in $repo_path..."
  git fetch -p

  echo "Finding local branches that no longer exist on the remote in $repo_path..."
  gone_branches=$(git for-each-ref --format '%(refname:short) %(upstream:track)' refs/heads | grep '\[gone\]' | awk '{print $1}')

  if [ -z "$gone_branches" ]; then
    echo "No local branches to delete in $repo_path."
  else
    echo "The following local branches will be deleted in $repo_path:"
    echo "$gone_branches"
    for branch in $gone_branches; do
      git branch -d "$branch" && echo "Deleted branch: $branch" || echo "Failed to delete branch: $branch"
    done
  fi
}

# Clean branches in the main repo
delete_removed_branches "."

# Check for submodules
if [ -f .gitmodules ]; then
  echo "Submodules detected. Cleaning branches in submodules..."

  # Loop through each submodule and clean its branches
  git submodule foreach --quiet '
    echo "Cleaning submodule: $name"
    delete_removed_branches "$(pwd)"
  '
else
  echo "No submodules detected."
fi
