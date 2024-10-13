#!/bin/bash

set -euo pipefail

branch="${1:-}"
if [ -z "$branch" ]; then
    echo "Error: Branch name not provided"
    exit 1
fi

# Checkout the specified branch
echo "Checking out branch ${branch}..."
git checkout "${branch}"

echo "Fetching changes from origin/${branch}..."
git fetch origin "${branch}"

# Ensure the branch is up to date
git pull origin "${branch}"

# Determine the current branch for context
current_branch=$(git rev-parse --abbrev-ref HEAD || echo "detached HEAD")
echo "Current branch: ${current_branch}"

# Get the list of changed files in the PR
changed_files=$(git diff --name-only origin/"${branch}" HEAD)
echo "Changed files in PR: ${changed_files}"

docs_changed="false"

# Check for changes in the main repository's documentation
if echo "$changed_files" | grep -q "applications/.*/docs/"; then
    docs_changed="true"
    echo "Documentation changes detected in the main repository."
fi

# Detect submodule commit changes
echo "Detecting submodule changes..."
cd ../../../../
submodule_updates=$(git diff --submodule=log origin/"${branch}" HEAD | grep "^Submodule")
echo ""
echo "$submodule_updates"
echo ""
while IFS= read -r line; do
  # Extract submodule path
  submodule_path=$(echo "$line" | awk '{print $2}')

  # Extract old and new SHA values
  SHAs=$(echo "$line" | awk -F' ' '{print $(NF)}' | sed 's/://')

  # Extract old and new SHAs
  old_sha="${SHAs%%..*}"
  new_sha="${SHAs##*..}"

  # Output the results
  echo "Checking submodule: $submodule_path"
  echo "Old SHA: $old_sha"
  echo "New SHA: $new_sha"

  # Ensure valid SHAs
  if [ -z "$old_sha" ] || [ -z "$new_sha" ]; then
      echo "Invalid SHA values for submodule $submodule_path, skipping."
      continue
  fi

  # Navigate to the submodule directory
  cd "$submodule_path" || continue

  # Fetch changes in the submodule
  git fetch

  # Check for documentation changes in the submodule between old and new SHA
  submodule_changes=$(git diff --name-only "$old_sha" "$new_sha" -- docs/)
  if [ -n "$submodule_changes" ]; then
      echo "Documentation changes detected in submodule $submodule_path:"
      echo "$submodule_changes"
      docs_changed="true"
  else
      echo "No documentation changes in submodule $submodule_path"
  fi

  # Return to the parent repository
  cd - > /dev/null
done <<< "$submodule_updates"

# Set the output for GitHub Actions
if [ -n "${GITHUB_OUTPUT:-}" ]; then
    echo "docs_modified=$docs_changed" >> "$GITHUB_OUTPUT"
else
    echo "GITHUB_OUTPUT is not set. For local testing, docs_modified=$docs_changed"
fi

echo "Final docs_modified value: $docs_changed"
