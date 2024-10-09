#!/bin/bash

# Set size limit (in bytes)
size_limit=10000000  # 10 MB

# Find large files
large_files=$(find . -type f -size +${size_limit}c)

if [ -n "$large_files" ]; then
  echo "Warning: The following files are larger than the size limit (${size_limit} bytes):"
  echo "$large_files"
else
  echo "No large files found."
fi
