#!/bin/bash

# Run branch clean-up
echo "Running branch clean-up..."
bash $(dirname "$0")/delete_merged_branches.sh

# Run large file check
echo "Running large file check..."
bash $(dirname "$0")/check_large_files.sh

echo "Clean-up completed."
