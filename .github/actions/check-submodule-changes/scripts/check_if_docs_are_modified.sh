#!/bin/bash

set -euo pipefail

branch="${1:-}"
if [ -z "$branch" ]; then
    echo "Error: Branch name not provided"
    exit 1
fi

echo "Fetching changes from origin/${branch}..."
git fetch origin "${branch}"

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

cd ../../../../
# Check for changes in submodules
while read -r submodule_path new_sha old_sha; do
    if [ -z "$new_sha" ] || [ -z "$old_sha" ]; then
        echo "Skipping submodule $submodule_path due to missing SHA"
        continue
    fi

    echo "Checking submodule: $submodule_path"
    echo "Old SHA: $old_sha"
    echo "New SHA: $new_sha"

    if [ "$new_sha" = "$old_sha" ]; then
        echo "No changes in submodule $submodule_path"
        continue
    fi

    # Navigate to the submodule directory
    cd "$submodule_path" || continue

    # Fetch the changes in the submodule
    git fetch

    # Check for changes in the docs folder between old and new SHA
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
done < <(git diff --submodule=short origin/"${branch}" HEAD | grep '^Subproject' | awk '{print $2, $3, $4}')

# Set the output for GitHub Actions
if [ -n "${GITHUB_OUTPUT:-}" ]; then
    echo "docs_modified=$docs_changed" >> "$GITHUB_OUTPUT"
else
    echo "GITHUB_OUTPUT is not set. For local testing, docs_modified=$docs_changed"
fi

echo "Final docs_modified value: $docs_changed"