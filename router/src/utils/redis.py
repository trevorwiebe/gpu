import redis
import os

def get_redis_client():
    # Use environment variables for flexibility
    # Default to host.docker.internal for Docker, but allow override for local dev
    host = os.getenv('REDIS_HOST', 'host.docker.internal')
    port = int(os.getenv('REDIS_PORT', '6379'))
    return redis.Redis(host=host, port=port, decode_responses=True)