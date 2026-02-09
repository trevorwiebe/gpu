#!/bin/bash

find_open_port() {
    local port=8001
    while true; do
        if ! lsof -i :$port > /dev/null 2>&1; then
            echo $port
            return
        fi
        port=$((port + 1))
    done
}

PORT=$(find_open_port)
NODE_NAME="node-$PORT"

docker run -d \
    --name "$NODE_NAME" \
    --hostname "$NODE_NAME" \
    --network gpu_gpu-net \
    --network-alias "$NODE_NAME" \
    -p $PORT:8005 \
    -e PUBLIC_IPADDR=localhost \
    -e EXTERNAL_PORT=$PORT \
    -e ROUTER_PUBLIC_IPADDR=localhost:5173 \
    gpu-node:latest
