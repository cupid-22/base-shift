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
    "gh-pages"
)

# Initialize arrays to track operations
declare -a deleted_branches=()
declare -a skipped_protected=()
declare -a skipped_current=()
declare -a failed_deletions=()

echo "Starting branch cleanup process..."
CLEANUP_MODE=$1
echo "Cleanup mode: ${CLEANUP_MODE}"

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
    # Check if we're in full cleanup mode
    if [[ "${CLEANUP_MODE}" == "full" ]]; then
        echo "Performing full cleanup..."

        # Process all remote branches
        echo "Processing remote branches..."
        readarray -t remote_branches < <(git branch -r | grep -v ' -> ' | sed 's/origin\///' | grep -vE "^($(IFS='|'; echo "${PROTECTED_PATTERNS[*]}"))")

        for branch in "${remote_branches[@]}"; do
            branch=$(echo "$branch" | xargs)  # Trim whitespace
            if [[ -n "$branch" ]] && evaluate_branch "$branch"; then
                delete_branch "$branch"
            fi
        done
    fi

    # Always process gone branches
    echo "Processing gone branches..."
    readarray -t gone_branches < <(git branch -vv | grep ': gone]' | awk '{print $1}')

    for branch in "${gone_branches[@]}"; do
        if evaluate_branch "$branch"; then
            echo "Deleting gone branch: $branch"
            delete_branch "$branch"
        fi
    done
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
