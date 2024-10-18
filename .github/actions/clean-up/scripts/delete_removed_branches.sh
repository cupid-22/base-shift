#!/bin/bash

# Set error handling and debug mode
set -euo pipefail

# GitHub API token should be set as environment variable GITHUB_TOKEN
if [ -z "${GITHUB_TOKEN:-}" ]; then
    echo "Error: GITHUB_TOKEN environment variable is not set"
    exit 1
fi

# Configuration
REPO="${GITHUB_REPOSITORY:-}"  # Format: owner/repo
GITHUB_API="https://api.github.com"

# Protected patterns (can be customized)
PROTECTED_PATTERNS=(
    "main"
    "master"
    "develop"
    "release/*"
    "hotfix/*"
)

echo "Starting enhanced branch cleanup process..."

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
        "$GITHUB_API/repos/$REPO/pulls?head=$REPO:$branch&state=open")
    [[ $response != "[]" ]]
}

# Function to check if PR is merged
is_pr_merged() {
    local pr_number=$1
    local response
    response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "$GITHUB_API/repos/$REPO/pulls/$pr_number")
    [[ $(echo "$response" | jq -r '.merged') == "true" ]]
}

# Function to get branch name from PR number
get_branch_from_pr() {
    local pr_number=$1
    local response
    response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "$GITHUB_API/repos/$REPO/pulls/$pr_number")
    echo "$response" | jq -r '.head.ref'
}

# Ensure we have latest remote information
git fetch --prune --all

# Get default and current branch
default_branch=$(git remote show origin | grep 'HEAD branch' | cut -d' ' -f5)
current_branch=$(git rev-parse --abbrev-ref HEAD)

echo "Default branch: $default_branch"
echo "Current branch: $current_branch"

# Handle specific PR if number is provided
if [ -n "${PR_NUMBER:-}" ]; then
    echo "Processing specific PR #$PR_NUMBER"
    branch=$(get_branch_from_pr "$PR_NUMBER")

    if [ -z "$branch" ]; then
        echo "Error: Could not find branch for PR #$PR_NUMBER"
        exit 1
    fi

    if has_active_pr "$branch"; then
        echo "Warning: PR #$PR_NUMBER is still active. Skipping cleanup."
        exit 0
    fi

    if ! is_pr_merged "$PR_NUMBER"; then
        echo "Warning: PR #$PR_NUMBER is not merged. Skipping cleanup."
        exit 0
    fi

    if is_protected "$branch"; then
        echo "Warning: Branch $branch matches protected pattern. Skipping cleanup."
        exit 0
    fi

    echo "Deleting branch: $branch"
    git branch -D "$branch" 2>/dev/null || true
    git push origin --delete "$branch" 2>/dev/null || true
    exit 0
fi

# Get all local branches
local_branches=$(git branch --format="%(refname:short)")

echo "Checking all local branches..."
for branch in $local_branches; do
    # Skip protected branches and patterns
    if is_protected "$branch"; then
        echo "Skipping protected branch: $branch"
        continue
    fi

    # Skip current branch
    if [ "$branch" = "$current_branch" ]; then
        echo "Skipping current branch: $branch"
        continue
    fi

    # Check for active PRs
    if has_active_pr "$branch"; then
        echo "Skipping branch with active PR: $branch"
        continue
    fi

    # Check if branch exists on remote
    if ! git ls-remote --heads origin "$branch" | grep -q "$branch"; then
        echo "Branch '$branch' no longer exists on remote - deleting..."
        git branch -D "$branch" || echo "Failed to delete branch: $branch"
    fi
done

# Handle merged/deleted remote branches
echo "Checking for merged/deleted remote branches..."
git fetch origin --prune

# Get and process branches with [gone] status
gone_branches=$(git branch -vv | grep ': gone]' | awk '{print $1}')

if [ -n "$gone_branches" ]; then
    echo "Found branches to delete:"
    echo "$gone_branches"

    echo "$gone_branches" | while read -r branch; do
        if ! is_protected "$branch" && [ "$branch" != "$current_branch" ]; then
            if ! has_active_pr "$branch"; then
                echo "Deleting gone branch: $branch"
                git branch -D "$branch" || echo "Failed to delete branch: $branch"
            else
                echo "Skipping gone branch with active PR: $branch"
            fi
        fi
    done
else
    echo "No additional gone branches found"
fi

echo "Branch cleanup completed"

# Print remaining branches for verification
echo "Remaining branches:"
git branch -a