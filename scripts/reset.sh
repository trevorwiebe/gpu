#!/bin/bash

./scripts/shutdown.sh

./scrupts/rebuild-router.sh

./scripts/rebuild-nodes.sh

./scripts/startup.sh