#!/bin/bash

# Set error handling
set -euo pipefail

# Configuration
PROTECTED_PATTERNS=(
    "main"
    "master"
    "develop"
    "release/*"
    "hotfix/*"
    "feature/*"  # Add any additional patterns
)

echo "Starting branch cleanup process..."
echo "Cleanup mode: ${CLEANUP_MODE:-selective}"

# Function to check if a branch matches any protected pattern
is_protected() {
    local branch=$1
    for pattern in "${PROTECTED_PATTERNS[@]}"; do
        if [[ $branch =~ $pattern ]]; then
            return 0
        fi
    done
    return 1
}

# Function to check if a PR exists for a branch
has_active_pr() {
    local branch=$1
    local response
    response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$GITHUB_REPOSITORY/pulls?head=$GITHUB_REPOSITORY:$branch&state=open")
    [[ $response != "[]" ]]
}

# Function to check if branch can be deleted
can_delete_branch() {
    local branch=$1

    # Skip protected branches
    if is_protected "$branch"; then
        echo "Protected branch: $branch - skipping"
        return 1
    fi

    # Skip branches with active PRs unless in full cleanup mode
    if [[ "${CLEANUP_MODE:-selective}" != "full" ]] && has_active_pr "$branch"; then
        echo "Branch has active PR: $branch - skipping"
        return 1
    fi

    # Check if branch exists on remote
    if git ls-remote --heads origin "$branch" | grep -q "$branch"; then
        echo "Branch still exists on remote: $branch - skipping"
        return 1
    fi

    return 0
}

# Ensure we have latest remote information
git fetch --prune --all

# Get default and current branch
default_branch=$(git remote show origin | grep 'HEAD branch' | cut -d' ' -f5)
current_branch=$(git rev-parse --abbrev-ref HEAD)

echo "Default branch: $default_branch"
echo "Current branch: $current_branch"

# Handle specific PR if number is provided
if [[ -n "${PR_NUMBER:-}" && "${CLEANUP_MODE:-selective}" != "full" ]]; then
    echo "Processing specific PR #$PR_NUMBER"
    branch=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$GITHUB_REPOSITORY/pulls/$PR_NUMBER" | \
        jq -r '.head.ref')

    if [[ -n "$branch" && "$branch" != "null" ]]; then
        if can_delete_branch "$branch"; then
            echo "Deleting branch for PR #$PR_NUMBER: $branch"
            git branch -D "$branch" 2>/dev/null || true
            git push origin --delete "$branch" 2>/dev/null || true
        fi
    else
        echo "Could not find branch for PR #$PR_NUMBER"
    fi
else
    echo "Performing ${CLEANUP_MODE:-selective} cleanup..."

    # Get all local branches
    local_branches=$(git branch --format="%(refname:short)")

    # Process each local branch
    for branch in $local_branches; do
        if [[ "$branch" != "$current_branch" && "$branch" != "$default_branch" ]]; then
            if can_delete_branch "$branch"; then
                echo "Deleting branch: $branch"
                git branch -D "$branch" 2>/dev/null || true
                git push origin --delete "$branch" 2>/dev/null || true
            fi
        fi
    done

    # Handle gone branches
    echo "Checking for gone branches..."
    gone_branches=$(git branch -vv | grep ': gone]' | awk '{print $1}')

    if [ -n "$gone_branches" ]; then
        echo "Processing gone branches..."
        echo "$gone_branches" | while read -r branch; do
            if can_delete_branch "$branch"; then
                echo "Deleting gone branch: $branch"
                git branch -D "$branch" 2>/dev/null || true
            fi
        done
    else
        echo "No gone branches found"
    fi
fi

echo "Cleanup completed"

# Print remaining branches for verification
echo "Remaining branches:"
git branch -a