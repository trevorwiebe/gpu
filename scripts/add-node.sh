#!/bin/bash

find_open_port() {
    local port=8006
    while true; do
        if ! lsof -i :$port > /dev/null 2>&1; then
            echo $port
            return
        fi
        port=$((port + 1))
    done
}

PORT=$(find_open_port)

docker run -d \
    --name "node-$PORT" \
    --network gpu_gpu-net \
    -p $PORT:8005 \
    -e ROUTER_API_KEY=secure-router-key-123 \
    gpu-node:latest

echo "Node started on port $PORT"
