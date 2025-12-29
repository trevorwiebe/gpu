import redis

def get_redis_client():
    return redis.Redis(host='host.docker.internal', port=6379, decode_responses=True)