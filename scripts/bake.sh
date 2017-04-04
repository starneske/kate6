#!/bin/bash
set -o allexport

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/..

if [ -e .env ]; then
	source .env
fi
echo $KATE6_DOCKER_IMAGE_LOCAL

docker build -t $KATE6_DOCKER_IMAGE_LOCAL:$KATE6_IMAGE_VERSION . 
