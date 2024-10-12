#!/bin/bash

set -euo pipefail  # Fail on error, unset variables, and command failures in pipelines

# Input branch for comparison
branch="${1}"

echo "Fetching changes from origin/${branch}..."
git fetch origin "${branch}"

# Show current branch for context
current_branch=$(git rev-parse --abbrev-ref HEAD || echo "detached HEAD")
echo "Current branch: ${current_branch}"

# Get changes in the main repository
changes=$(git diff --name-only origin/"${branch}" HEAD)

# Debugging output for detected changes in the main repository
echo "Changes detected in the main repo: $changes"  # Log changes

# Initialize docs_changed variable
docs_changed="false"

# Check if there are any changes in the documentation directories in the main repository
if echo "$changes" | grep -q "applications/.*/docs/"; then
  docs_changed="true"
  echo "Documentation directories have changes in the main repo."
else
  echo "No changes in documentation directories in the main repo."
fi

cd ../../../../
# Detect submodules with new commit references
echo "Discovering submodules with changed commit references..."
changed_submodules=$(git diff --submodule=log origin/"${branch}" HEAD | grep "^Submodule" | awk '{print $2}')

echo "Submodules with changed commits: $changed_submodules"

# Iterate over changed submodules and check for doc changes
for submodule in $changed_submodules; do
  echo ""
  echo "Checking submodule: $submodule"
  git submodule update --init --remote "$submodule"  # Ensure the submodule is updated

  submodule_changes=$(git diff --name-only origin/"${branch}" "$submodule")
  echo ""
  # Debugging output for detected changes in the submodule
  echo "Changes detected in submodule $submodule: $submodule_changes"
  echo ""
  if echo "$submodule_changes" | grep -q "docs/"; then
    docs_changed="true"
    echo "Glad, Found Documentation directories that have changes in $submodule"
    break  # Exit the loop if changes are found
  else
    echo "But, No changes detected in $submodule documentation."
  fi
done

GITHUB_ENV=false
# Set the GITHUB_ENV variable based on findings
if [ "$docs_changed" == "true" ]; then
  echo "docs_modified=true" >> "$GITHUB_ENV"
else
  echo "docs_modified=false" >> "$GITHUB_ENV"
fi

# Log final output for debugging
echo "Final docs_modified value: $docs_changed: $GITHUB_ENV"
