from fastapi import APIRouter, HTTPException
import redis

from models.node import AuthenticateNodeRequest

router = APIRouter(
    prefix="/user/me",
    tags=["nodes"]
)

@router.get("/nodes")
async def get_nodes(userId: str):
    """Get the user's node"""

    try:
        return {"status": "success"}
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

        # Store node information in Redis
        node_data = {
            "nodeId": node_id,
            "userId": request.userId,
            "status": "active"
        }

        # Store node data
        client.hset(f'node:{node_id}', mapping=node_data)

        # Add node to user's nodes set
        client.sadd(f'user:{request.userId}:nodes', node_id)

        # Delete the setup token as it's been used
        client.delete(f'setup_token:{request.setupToken}')

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