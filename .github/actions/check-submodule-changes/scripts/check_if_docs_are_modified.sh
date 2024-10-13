#!/bin/bash

set -euo pipefail

branch="${1:-}"
if [ -z "$branch" ]; then
    echo "Error: Branch name not provided"
    exit 1
fi

echo "Fetching changes from origin/${branch}..."
git fetch origin "${branch}"

# Initialize and update submodules
git submodule init
git submodule update --recursive

# Ensure each submodule is on the correct branch or HEAD state
git submodule foreach "
    echo 'Checking out correct branch for submodule...'
    branch_name=\$(git symbolic-ref --short HEAD || echo 'main')
    git fetch origin
    git checkout \${branch_name} || git checkout \${branch}
    git pull origin \${branch_name} || true
"

# Determine the current branch for context
current_branch=$(git rev-parse --abbrev-ref HEAD || echo "detached HEAD")
echo "Current branch: ${current_branch}"

echo "Detecting submodule changes..."
submodule_changes=$(git diff --submodule=log origin/"${branch}" HEAD)

docs_changed="false"

cd ../../../../
# Process each changed submodule
while IFS= read -r line; do
    submodule_path=$(echo "$line" | awk '{print $2}')
    sha_changes=$(echo "$line" | awk '{print $3}' | sed 's/://')
    old_sha=$(echo "$sha_changes" | cut -d'.' -f1)
    new_sha=$(echo "$sha_changes" | cut -d'.' -f3)

    echo "Checking submodule: $submodule_path"
    echo "Old SHA: $old_sha"
    echo "New SHA: $new_sha"

    # Navigate to the submodule directory
    cd "$submodule_path" || continue

    # Fetch changes in the submodule
    git fetch

    # Check for documentation changes in the submodule between old and new SHA
    if [ -n "$old_sha" ] && [ -n "$new_sha" ] && [ "$old_sha" != "$new_sha" ]; then
        submodule_doc_changes=$(git diff --name-only "$old_sha" "$new_sha" -- docs/)
        if [ -n "$submodule_doc_changes" ]; then
            echo "Documentation changes detected in submodule $submodule_path:"
            echo "$submodule_doc_changes"
            docs_changed="true"
        else
            echo "No documentation changes in submodule $submodule_path"
        fi
    else
        echo "Unable to compare changes in submodule $submodule_path"
    fi

    # Return to the parent repository
    cd - > /dev/null
done <<< "$(echo "$submodule_changes" | grep '^Submodule')"

# Set the output for GitHub Actions
if [ -n "${GITHUB_OUTPUT:-}" ]; then
    echo "docs_modified=$docs_changed" >> "$GITHUB_OUTPUT"
else
    echo "GITHUB_OUTPUT is not set. For local testing, docs_modified=$docs_changed"
fi

echo "Final docs_modified value: $docs_changed"
