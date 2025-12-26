from fastapi import APIRouter, HTTPException
import redis

from models.node import AuthenticateNodeRequest

router = APIRouter(
    prefix="/user/me",
    tags=["nodes"]
)

@router.get("/nodes")
async def get_nodes(userId: str):
    """Get all nodes for a user with their information"""

    try:
        client = redis.Redis(host='host.docker.internal', port=6379, decode_responses=True)

        # Get all node IDs for this user
        node_ids = client.smembers(f'user:{userId}:nodes')

        if not node_ids:
            return []

        # Fetch data for each node
        nodes = []
        for node_id in node_ids:
            node_data = client.hgetall(f'node:{node_id}')

            if node_data:
                # Include the node_id in the response
                node_data['nodeId'] = node_id
                nodes.append(node_data)

        return nodes

    except redis.exceptions.ConnectionError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Redis service unavailable: {str(e)}"
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        ) from e
    
@router.post("/node/authenticate")
async def authenticate_node(request: AuthenticateNodeRequest):
    """Authenticate a node with a setup token"""
    try:
        client = redis.Redis(host='host.docker.internal', port=6379, decode_responses=True)

        # Verify the setup token exists and get the node_id
        node_id = client.get(f'setup_token:{request.setupToken}')

        if not node_id:
            raise HTTPException(
                status_code=404,
                detail="Invalid or expired setup token"
            )

        # Retrieve the node name
        node_name = client.get(f'setup_token_name:{request.setupToken}')

        # Ensure node name is unique for this user
        existing_node_ids = client.smembers(f'user:{request.userId}:nodes')
        existing_names = set()

        for existing_node_id in existing_node_ids:
            existing_node_data = client.hgetall(f'node:{existing_node_id}')
            if existing_node_data and 'nodeName' in existing_node_data:
                existing_names.add(existing_node_data['nodeName'])

        # If name already exists, append a number to make it unique
        if node_name in existing_names:
            counter = 2
            while f"{node_name}-{counter}" in existing_names:
                counter += 1
            node_name = f"{node_name}-{counter}"

        # Store node information in Redis
        node_data = {
            "nodeId": node_id,
            "userId": request.userId,
            "status": "active",
            "nodeName": node_name
        }

        # Store node data
        client.hset(f'node:{node_id}', mapping=node_data)

        # Add node to user's nodes set
        client.sadd(f'user:{request.userId}:nodes', node_id)

        # Delete the setup token and node name as they've been used
        client.delete(f'setup_token:{request.setupToken}')
        client.delete(f'setup_token_name:{request.setupToken}')

        return {
            "status": "success",
            "message": "Node authenticated successfully",
            "nodeId": node_id
        }

    except redis.exceptions.ConnectionError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Redis service unavailable: {str(e)}"
        ) from e
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Authentication failed: {str(e)}"
        ) from e