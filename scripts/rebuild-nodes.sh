#!/bin/bash

docker ps -a --filter "name=node-" --format "{{.Names}}" | xargs -r docker rm -f 2>/dev/null

docker-compose stop node
docker-compose rm -f node

redis-cli -h localhost -p 6379 --scan --pattern "node:*" | xargs -r redis-cli -h localhost -p 6379 del 2>/dev/null
redis-cli -h localhost -p 6379 --scan --pattern "user:*:nodes" | xargs -r redis-cli -h localhost -p 6379 del 2>/dev/null
redis-cli -h localhost -p 6379 --scan --pattern "setup_token:*" | xargs -r redis-cli -h localhost -p 6379 del 2>/dev/null
redis-cli -h localhost -p 6379 --scan --pattern "setup_token_name:*" | xargs -r redis-cli -h localhost -p 6379 del 2>/dev/null

docker-compose build node
docker-compose up -d node

echo "All nodes killed, rebuilt with 1 node"
