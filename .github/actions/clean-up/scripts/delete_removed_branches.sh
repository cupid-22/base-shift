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
)

# Initialize arrays to track operations
declare -a deleted_branches=()
declare -a skipped_protected=()
declare -a skipped_current=()
declare -a failed_deletions=()

echo "Starting branch cleanup process..."
CLEANUP_MODE=$1
PR_NUMBER=$2
echo "Cleanup mode: ${CLEANUP_MODE}"
echo "PR if provided: ${PR_NUMBER}"

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

# Function to delete branch
delete_branch() {
    local branch=$1
    local success=true

    echo "Attempting to delete branch: $branch"

    # Delete local branch if it exists
    if git branch --list "$branch" | grep -q "$branch"; then
        if git branch -D "$branch" 2>/dev/null; then
            echo "Deleted local branch: $branch"
        else
            echo "Failed to delete local branch: $branch"
            success=false
        fi
    fi

    # Delete remote branch if it exists
    if git ls-remote --heads origin "$branch" | grep -q "$branch"; then
        if git push origin --delete "$branch" 2>/dev/null; then
            echo "Deleted remote branch: $branch"
        else
            echo "Failed to delete remote branch: $branch"
            success=false
        fi
    fi

    if $success; then
        deleted_branches+=("$branch")
    else
        failed_deletions+=("$branch")
    fi
}

# Function to check if branch can be deleted
evaluate_branch() {
    local branch=$1

    # Remove 'remotes/origin/' prefix if present
    branch=${branch#remotes/origin/}

    # Skip if branch is current
    if [[ "$branch" == "$current_branch" ]]; then
        echo "Skipping current branch: $branch"
        skipped_current+=("$branch")
        return 1
    fi

    # Skip if branch is protected
    if is_protected "$branch"; then
        echo "Skipping protected branch: $branch"
        skipped_protected+=("$branch")
        return 1
    fi

    return 0
}

# Main cleanup function
main() {
    # Ensure we have latest remote information
    echo "Fetching latest remote information..."
    git fetch --prune --all

    # Get current branch
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    echo "Current branch: $current_branch"

    # Check cleanup mode from environment variable
    if [[ "${CLEANUP_MODE:-selective}" == "full" ]]; then
        echo "Performing full cleanup..."

        # Process all remote branches
        echo "Processing remote branches..."
        while IFS= read -r branch; do
            branch=$(echo "$branch" | xargs)  # Trim whitespace
            if [[ -n "$branch" ]] && evaluate_branch "$branch"; then
                delete_branch "$branch"
            fi
        done < <(git branch -r | grep -v ' -> ' | sed 's/origin\///' | grep -vE "^($(IFS='|'; echo "${PROTECTED_PATTERNS[*]}"))")
    else
        # Handle specific PR if number is provided
        echo "Performing selective cleanup of gone branches only..."
        if [[ -n "${PR_NUMBER:-}" && "$PR_NUMBER" != "full-cleanup" ]]; then
            echo "Processing specific PR #$PR_NUMBER"
            branch=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
                "https://api.github.com/repos/$GITHUB_REPOSITORY/pulls/$PR_NUMBER" | \
                jq -r '.head.ref')

            if [[ -n "$branch" && "$branch" != "null" ]]; then
                if evaluate_branch "$branch"; then
                    delete_branch "$branch"
                fi
            else
                echo "Could not find branch for PR #$PR_NUMBER"
            fi
        else
            echo "Maybe was for the full-cleanup..."
        fi
    fi

    # Always process gone branches
    echo "Processing gone branches..."
    while IFS= read -r branch; do
        if evaluate_branch "$branch"; then
            echo "Deleting gone branch: $branch"
            delete_branch "$branch"
        fi
    done < <(git branch -vv | grep ': gone]' | awk '{print $1}')
}

# Run main cleanup
main

# Print summary
echo "🧹 Cleanup Summary:"
echo "===================="

echo "✅ Successfully deleted branches (${#deleted_branches[@]}):"
if [ ${#deleted_branches[@]} -eq 0 ]; then
    echo "   None"
else
    printf '   - %s\n' "${deleted_branches[@]}"
fi

echo -e "\n❌ Failed deletions (${#failed_deletions[@]}):"
if [ ${#failed_deletions[@]} -eq 0 ]; then
    echo "   None"
else
    printf '   - %s\n' "${failed_deletions[@]}"
fi

echo -e "\n⏩ Skipped branches:"
echo "   Protected (${#skipped_protected[@]}):"
if [ ${#skipped_protected[@]} -eq 0 ]; then
    echo "   None"
else
    printf '   - %s\n' "${skipped_protected[@]}"
fi

echo "   Current branch (${#skipped_current[@]}):"
if [ ${#skipped_current[@]} -eq 0 ]; then
    echo "   None"
else
    printf '   - %s\n' "${skipped_current[@]}"
fi

# List remaining branches
echo -e "\nRemaining branches:"
git branch -a
