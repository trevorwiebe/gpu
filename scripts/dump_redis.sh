#!/bin/bash

# Check if redis-cli is available
if ! command -v redis-cli &> /dev/null; then
    echo "Error: redis-cli not found. Please install Redis tools."
    echo "  macOS: brew install redis"
    echo "  Ubuntu: sudo apt-get install redis-tools"
    exit 1
fi

# Test connection
if ! redis-cli -h localhost -p 6379 ping > /dev/null 2>&1; then
    echo "✗ Error: Could not connect to Redis at localhost:6379"
    echo "  Make sure Redis is running and accessible"
    exit 1
fi

# Get current key count
KEY_COUNT=$(redis-cli -h localhost -p 6379 DBSIZE | awk '{print $NF}')
echo "Total keys in database: $KEY_COUNT"
echo "--------------------------------------------------"

if [ "$KEY_COUNT" -eq 0 ]; then
    echo "✓ Database is empty - no keys found"
    exit 0
fi

# Dump all keys and their values
redis-cli -h localhost -p 6379 KEYS '*' | sort | while read key; do
    # Get the type of the key
    TYPE=$(redis-cli -h localhost -p 6379 TYPE "$key")

    echo "Key: $key"

    # Get value based on type
    case $TYPE in
        string)
            VALUE=$(redis-cli -h localhost -p 6379 GET "$key")
            echo "Value($TYPE): $VALUE"
            ;;
        list)
            echo "Value ($TYPE): $VALUE"
            redis-cli -h localhost -p 6379 LRANGE "$key" 0 -1 | sed 's/^/  /'
            ;;
        set)
            echo "Value ($TYPE): $VALUE"
            redis-cli -h localhost -p 6379 SMEMBERS "$key" | sed 's/^/  /'
            ;;
        zset)
            echo "Value ($TYPE): $VALUE"
            redis-cli -h localhost -p 6379 ZRANGE "$key" 0 -1 WITHSCORES | paste - - | sed 's/^/  /' | sed 's/\t/ (score: /' | sed 's/$/)/'
            ;;
        hash)
            echo "Value ($TYPE): $VALUE"
            redis-cli -h localhost -p 6379 HGETALL "$key" | paste - - | sed 's/^/  /' | sed 's/\t/: /'
            ;;
        *)
            echo "Value: Unknown type"
            ;;
    esac

    echo "--------------------------------------------------"
done

echo ""
echo "✓ Dumped $KEY_COUNT keys from Redis database"
