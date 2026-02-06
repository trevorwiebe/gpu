#!/bin/bash

docker-compose up -d

cd front-end && npm run dev
