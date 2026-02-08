#!/bin/bash

# Capture running node containers and their ports before stopping
NODES=()
for container in $(docker ps --filter "name=node-" --format "{{.Names}}"); do
    PORT=$(echo "$container" | sed 's/node-//')
    NODES+=("$PORT")
done

# Stop and remove all node containers
docker ps -a --filter "name=node-" --format "{{.Names}}" | xargs -r docker rm -f 2>/dev/null

# Clean up Redis keys
redis-cli -h localhost -p 6379 --scan --pattern "node:*" | xargs -r redis-cli -h localhost -p 6379 del 2>/dev/null
redis-cli -h localhost -p 6379 --scan --pattern "user:*:nodes" | xargs -r redis-cli -h localhost -p 6379 del 2>/dev/null
redis-cli -h localhost -p 6379 --scan --pattern "setup_token:*" | xargs -r redis-cli -h localhost -p 6379 del 2>/dev/null
redis-cli -h localhost -p 6379 --scan --pattern "setup_token_name:*" | xargs -r redis-cli -h localhost -p 6379 del 2>/dev/null

# Rebuild the node image
docker build -t gpu-node:latest ./node

# Restart the nodes that were previously running
for PORT in "${NODES[@]}"; do
    NODE_NAME="node-$PORT"
    docker run -d \
        --name "$NODE_NAME" \
        --hostname "$NODE_NAME" \
        --network gpu_gpu-net \
        --network-alias "$NODE_NAME" \
        -p $PORT:8005 \
        gpu-node:latest
done
