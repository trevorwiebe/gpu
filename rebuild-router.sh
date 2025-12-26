#!/bin/bash

docker-compose stop router
docker-compose rm -f router
docker-compose build router
docker-compose up -d router
