#!/bin/bash

# Get the current directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$DIR/.."

# Load .env file
export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs)

cd "$PROJECT_DIR"

if [ "$ENV" == "Prod" ]; then
  COMPOSE_FILE="docker-compose-prod.yml"
else
  COMPOSE_FILE="docker-compose.yml"
fi

docker-compose -f $COMPOSE_FILE build --pull
docker-compose -f $COMPOSE_FILE up -d --remove-orphans
