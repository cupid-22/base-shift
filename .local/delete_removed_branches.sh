#!/bin/bash

# Fetch and prune remote branches
git fetch -p

# Find and delete only fully merged local branches that no longer exist on the remote
git branch -vv | grep ': gone]' | grep -v '\[origin' | awk '{print $1}' | xargs -r git branch -d
