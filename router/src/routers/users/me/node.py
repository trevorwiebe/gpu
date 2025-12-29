from fastapi import APIRouter, HTTPException
import redis

from models.node import AuthenticateNodeRequest, AssignModelToNodeRequest
from utils.crypto import generate_node_api_key

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

                # Include assigned models
                assigned_models = client.smembers(f'node:{node_id}:models')
                node_data['assignedModels'] = list(assigned_models) if assigned_models else []

                # Ensure model status fields exist (backward compatibility)
                if 'modelStatus' not in node_data:
                    node_data['modelStatus'] = 'idle'
                if 'activeModel' not in node_data:
                    node_data['activeModel'] = ''
                if 'activeModelName' not in node_data:
                    node_data['activeModelName'] = ''

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

        # Generate unique API key for this node
        node_api_key = generate_node_api_key(node_id)

        # Store node information in Redis
        node_data = {
            "nodeId": node_id,
            "userId": request.userId,
            "status": "active",
            "nodeName": node_name,
            "modelStatus": "idle",
            "activeModel": "",
            "activeModelName": "",
            "apiKey": node_api_key
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

@router.post("/node/assign-model")
async def assign_model_to_node(request: AssignModelToNodeRequest):
    """Assign a model from the user's library to a node"""
    try:
        client = redis.Redis(host='host.docker.internal', port=6379, decode_responses=True)

        # Verify node exists
        node_data = client.hgetall(f'node:{request.nodeId}')
        if not node_data:
            raise HTTPException(
                status_code=404,
                detail="Node not found"
            )
        
        # Verify user owns the node
        user_nodes = client.smembers(f'user:{request.userId}:nodes')
        if request.nodeId not in user_nodes:
            raise HTTPException(
                status_code=404,
                detail="User does not own this node"
            )

        # Verify model exists
        model_data = client.hgetall(f'model:{request.modelId}')
        if not model_data:
            raise HTTPException(
                status_code=404,
                detail="Model not found"
            )
        
        # Verify the model is in the users library
        user_models = client.smembers(f'user:{request.userId}:models')
        if request.modelId not in user_models:
            raise HTTPException(
                status_code=404,
                detail="Model not found in user's library"
            )

        # Check if model is already assigned to this node
        if client.sismember(f'node:{request.nodeId}:models', request.modelId):
            raise HTTPException(
                status_code=400,
                detail="Model is already assigned to this node"
            )

        # Assign the model to the node (using a set to support multiple models)
        client.sadd(f'node:{request.nodeId}:models', request.modelId)

        return {
            "status": "success",
            "message": "Model assigned to node successfully",
            "nodeId": request.nodeId,
            "modelId": request.modelId
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
            detail=f"An unexpected error occurred: {str(e)}"
        ) from e