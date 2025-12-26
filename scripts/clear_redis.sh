#!/bin/bash

# Script to clear Redis database used by both router and node services
# This will remove all authentication tokens, node registrations, and user associations

echo "Redis Database Cleaner"
echo "=================================================="

# Check if redis-cli is available
if ! command -v redis-cli &> /dev/null; then
    echo "Error: redis-cli not found. Please install Redis tools."
    echo "  macOS: brew install redis"
    echo "  Ubuntu: sudo apt-get install redis-tools"
    exit 1
fi

# Test connection
echo "Testing connection to Redis..."
if ! redis-cli -h localhost -p 6379 ping > /dev/null 2>&1; then
    echo "✗ Error: Could not connect to Redis at localhost:6379"
    echo "  Make sure Redis is running and accessible"
    exit 1
fi

echo "✓ Connected to Redis successfully"

# Get current key count
KEY_COUNT=$(redis-cli -h localhost -p 6379 DBSIZE | awk '{print $NF}')
echo "Current keys in database: $KEY_COUNT"

if [ "$KEY_COUNT" -eq 0 ]; then
    echo "✓ Database is already empty"
    exit 0
fi

# Show what keys exist
echo ""
echo "Keys to be deleted:"
redis-cli -h localhost -p 6379 KEYS '*' | while read key; do
    echo "  - $key"
done

# Ask for confirmation
echo ""
read -p "Are you sure you want to delete all $KEY_COUNT keys? (yes/no): " response

if [[ ! "$response" =~ ^[Yy](es)?$ ]]; then
    echo "Operation cancelled"
    exit 0
fi

# Clear all keys
redis-cli -h localhost -p 6379 FLUSHDB > /dev/null
echo ""
echo "✓ Successfully cleared $KEY_COUNT keys from Redis database"
echo "✓ All setup tokens, node registrations, and user data have been removed"
