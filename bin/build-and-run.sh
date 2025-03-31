#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR=$DIR/..

cd $PROJECT_DIR

docker-compose -f docker-compose-prod.yml build --pull
docker-compose -f docker-compose-prod.yml up -d --remove-orphans
