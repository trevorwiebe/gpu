#!/bin/bash

# Rebuild and start Docker services
./rebuild-docker.sh &

# Start Redis
redis-server &

# Start front-end
cd front-end && npm run dev
