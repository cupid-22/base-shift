#!/bin/bash

# Load the .env file
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Replace the placeholder with the actual token
sed "s/\${SONARQUBE_TOKEN}/$SONARQUBE_TOKEN/g" .local/sonarlint.template.json > .sonarlint/conf/sonarlint.json
