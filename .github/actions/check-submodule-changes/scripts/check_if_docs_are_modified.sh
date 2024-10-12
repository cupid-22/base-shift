#!/bin/bash

set -euo pipefail  # Fail on error, unset variables, and command failures in pipelines

# Input branch for comparison
branch="${1}"

echo "Fetching changes from origin/${branch}..."
git fetch origin "${branch}"

# Show current branch for context
current_branch=$(git rev-parse --abbrev-ref HEAD)
echo "Current branch: ${current_branch}"

# Get changes between the fetched branch and the current HEAD
changes=$(git diff --name-only origin/"${branch}" HEAD)

# Debugging output for detected changes
if [[ -z "$changes" ]]; then
  echo "No changes detected."
else
  echo "Changes detected: $changes"
fi

# Check if there are any changes in the documentation directories
docs_changed=$(echo "$changes" | grep -E "applications/.*/docs")

# Output debugging info for matched changes
if [ -n "$docs_changed" ]; then
  echo "Documentation directories have changes:"
  echo "$docs_changed"
  echo "docs_modified=true" >> "$GITHUB_ENV"
else
  echo "No changes in documentation directories."
  echo "docs_modified=false" >> "$GITHUB_ENV"
fi

# Log final output for debugging
echo "Final docs_modified value: ${docs_modified:-not set}"
