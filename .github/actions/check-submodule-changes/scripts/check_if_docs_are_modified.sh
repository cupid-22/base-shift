#!/bin/bash

set -euo pipefail

branch="${1:-}"
if [ -z "$branch" ]; then
    echo "Error: Branch name not provided"
    exit 1
fi

echo "Fetching changes from origin/${branch}..."
git fetch origin "${branch}"

# Determine the current branch for context
current_branch=$(git rev-parse --abbrev-ref HEAD || echo "detached HEAD")
echo "Current branch: ${current_branch}"

echo "Detecting submodule changes..."
submodule_changes=$(git diff --submodule=log origin/"${branch}" HEAD)

docs_changed=false

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
    echo "Current Directory: $(pwd)"
    cd "$submodule_path" || continue

    # Check for detached HEAD state and handle accordingly
    submodule_branch=$(git rev-parse --abbrev-ref HEAD || echo "detached HEAD")
    if [ "$submodule_branch" == "detached HEAD" ]; then
        echo "Currently in detached HEAD state for $submodule_path, skipping pull."
    else
        if git status | grep -q "Your branch and 'origin/${branch}' have diverged"; then
            echo "Branches have diverged. Attempting to rebase."
            git fetch origin
            git rebase origin/"${branch}"
        else
            git pull origin "${branch}"
        fi
    fi

    # Fetch changes in the submodule
    git fetch

    # Check for documentation changes in the submodule between old and new SHA
    if [ -n "$old_sha" ] && [ -n "$new_sha" ] && [ "$old_sha" != "$new_sha" ]; then
        submodule_doc_changes=$(git diff --name-only "$old_sha" "$new_sha" -- docs/)
        if [ -n "$submodule_doc_changes" ]; then
            echo "Documentation changes detected in submodule $submodule_path:"
            echo "$submodule_doc_changes"
            docs_changed=true
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
