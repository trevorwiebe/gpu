import secrets

def generate_node_api_key(node_id: str) -> str:
    """
    Generate a secure, unique API key for a node.
    Format: "node_<node_id_prefix>_<random_hex>"

    Args:
        node_id: The node's UUID

    Returns:
        A secure API key string (e.g., "node_a1b2c3d4_f7e8d9c0b1a2...")
    """
    node_prefix = node_id[:8]
    random_bytes = secrets.token_bytes(32)
    random_hex = random_bytes.hex()
    return f"node_{node_prefix}_{random_hex}"
