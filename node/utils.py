import redis
import logging
import os
from typing import Optional

def get_redis_client():
    # Use environment variables for flexibility
    # Default to host.docker.internal for Docker, but allow override for local dev
    host = os.getenv('REDIS_HOST', 'host.docker.internal')
    port = int(os.getenv('REDIS_PORT', '6379'))
    return redis.Redis(host=host, port=port, decode_responses=True)

def update_node_status_in_redis(node_id: str, status: str, model_id: str = "", model_name: str = ""):
    try:
        client = get_redis_client()
        client.hset(f'node:{node_id}', mapping={
            "modelStatus": status,
            "activeModelId": model_id,
            "activeModelName": model_name
        })
        logging.debug(f"Updated Redis: modelStatus={status}, activeModelId={model_id}")
    except Exception as e:
        logging.warning(f"Failed to update Redis with status '{status}': {e}")

def is_node_authenticated(node_id: str) -> bool:
    try:
        client = get_redis_client()
        node_data = client.hgetall(f'node:{node_id}')
        return bool(node_data and node_data.get('userId'))
    except Exception as e:
        logging.warning(f"Failed to check authentication status: {e}")
        return False

def get_node_user_id(node_id: str) -> Optional[str]:
    try:
        client = get_redis_client()
        node_data = client.hgetall(f'node:{node_id}')
        return node_data.get('userId')
    except Exception as e:
        logging.warning(f"Failed to get user ID: {e}")
        return None

def get_node_api_key(node_id: str) -> Optional[str]:
    try:
        client = get_redis_client()
        node_data = client.hgetall(f'node:{node_id}')
        return node_data.get('apiKey')
    except Exception as e:
        logging.warning(f"Failed to get API key: {e}")
        return None

def get_node_details(node_id: str) -> dict:
    try:
        client = get_redis_client()
        node_data = client.hgetall(f'node:{node_id}')
        return node_data
    except Exception as e:
        logging.warning(f"Failed to get node details: {e}")
        return {}

