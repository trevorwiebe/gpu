#!/bin/bash

docker-compose up -d

redis-server &

cd front-end && npm run dev
