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
declare -a skipped_active_pr=()
declare -a skipped_current=()
declare -a failed_deletions=()

# Set defaults and handle inputs
CLEANUP_MODE=${CLEANUP_MODE:-selective}
PR_NUMBER=${PR_NUMBER:-""}

echo "Starting branch cleanup process..."
echo "Cleanup mode: $CLEANUP_MODE"
echo "PR number: ${PR_NUMBER:-none}"

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
    if [[ -z "${GITHUB_TOKEN:-}" ]]; then
        echo "Warning: GITHUB_TOKEN not set, skipping PR check"
        return 1
    }

    local response
    response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$GITHUB_REPOSITORY/pulls?head=$GITHUB_REPOSITORY:$branch&state=open")
    [[ $response != "[]" ]]
}

# Function to delete branch
delete_branch() {
    local branch=$1
    local success=true

    echo "Attempting to delete branch: $branch"

    # Try to delete local branch
    if git branch -D "$branch" 2>/dev/null; then
        echo "Deleted local branch: $branch"
    else
        echo "Failed to delete local branch: $branch"
        success=false
    fi

    # Try to delete remote branch if it exists
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

    if [[ "$branch" == "$current_branch" ]]; then
        echo "Skipping current branch: $branch"
        skipped_current+=("$branch")
        return 1
    fi

    if is_protected "$branch"; then
        echo "Skipping protected branch: $branch"
        skipped_protected+=("$branch")
        return 1
    fi

    if [[ "$CLEANUP_MODE" != "full" ]] && has_active_pr "$branch"; then
        echo "Skipping branch with active PR: $branch"
        skipped_active_pr+=("$branch")
        return 1
    fi

    return 0
}

# Main cleanup logic
main() {
    # Ensure we have latest remote information
    git fetch --prune --all

    # Get default and current branch
    default_branch=$(git remote show origin | grep 'HEAD branch' | cut -d' ' -f5)
    current_branch=$(git rev-parse --abbrev-ref HEAD)

    echo "Default branch: $default_branch"
    echo "Current branch: $current_branch"

    # Handle specific PR if number is provided
    if [[ -n "$PR_NUMBER" && "$PR_NUMBER" != "full-cleanup" ]]; then
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
        return
    fi

    # Get all local branches
    readarray -t local_branches < <(git branch --format="%(refname:short)")

    # Process branches based on cleanup mode
    if [[ "$CLEANUP_MODE" == "full" ]]; then
        echo "Performing full cleanup..."
        for branch in "${local_branches[@]}"; do
            if evaluate_branch "$branch"; then
                delete_branch "$branch"
            fi
        done
    fi

    # Always check for gone branches
    echo "Checking for gone branches..."
    readarray -t gone_branches < <(git branch -vv | grep ': gone]' | awk '{print $1}')

    for branch in "${gone_branches[@]}"; do
        if evaluate_branch "$branch"; then
            delete_branch "$branch"
        fi
    done
}

# Run main function
main

# Print summary
print_summary() {
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

    echo "   Active PRs (${#skipped_active_pr[@]}):"
    if [ ${#skipped_active_pr[@]} -eq 0 ]; then
        echo "   None"
    else
        printf '   - %s\n' "${skipped_active_pr[@]}"
    fi

    echo "   Current branch (${#skipped_current[@]}):"
    if [ ${#skipped_current[@]} -eq 0 ]; then
        echo "   None"
    else
        printf '   - %s\n' "${skipped_current[@]}"
    fi
}

print_summary

# List remaining branches
echo -e "\nRemaining branches:"
git branch -a