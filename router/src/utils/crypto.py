import secrets

def generate_node_api_key(node_id: str) -> str:
    node_prefix = node_id[:8]
    random_bytes = secrets.token_bytes(32)
    random_hex = random_bytes.hex()
    return f"node_{node_prefix}_{random_hex}"
