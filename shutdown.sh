#!/bin/bash

./clear_redis.sh

docker ps -a --filter "name=node-" --format "{{.Names}}" | xargs -r docker rm -f 2>/dev/null

docker-compose down

pkill redis-server 2>/dev/null
