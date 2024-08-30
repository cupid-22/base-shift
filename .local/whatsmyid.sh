#!/usr/bin/env bash

echo "v$(echo "refs/heads/$(git rev-parse --abbrev-ref HEAD)" | md5sum | head -c 6)"