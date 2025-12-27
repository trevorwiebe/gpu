#!/bin/bash

# Docker logs script - Follow all container logs in real-time

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting docker logs for all containers...${NC}"
echo -e "${BLUE}Press Ctrl+C to stop${NC}"
echo ""

# Check if docker compose is available
if command -v docker compose &> /dev/null; then
    # Use docker compose (newer syntax)
    docker compose logs -f "$@"
elif command -v docker-compose &> /dev/null; then
    # Use docker-compose (older syntax)
    docker-compose logs -f "$@"
else
    echo "Error: Neither 'docker compose' nor 'docker-compose' is available"
    exit 1
fi
