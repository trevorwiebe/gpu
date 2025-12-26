from fastapi import APIRouter, HTTPException
import redis
from pydantic import BaseModel

from models.library import SetModelRequest

router = APIRouter(
    prefix="/user/me",
    tags=["library"]
)

@router.post("/library")
async def set_model(request: SetModelRequest):
    """Set model in hosting library"""
    try:
        client = redis.Redis(host='host.docker.internal', port=6379, decode_responses=True)

        if request.isSet:
            # Use pipeline to update both the model hash AND the user's set
            pipe = client.pipeline()
            pipe.hset(
                f'model:{request.modelId}',
                mapping={
                    "id": request.modelId,
                    "userId": request.userId,
                    "modelId": request.modelId,
                    "health": "active"
                }
            )
            pipe.sadd(f'user:{request.userId}:models', request.modelId)
            pipe.execute()
        else:
            # Remove from both the model hash AND the user's set
            pipe = client.pipeline()
            pipe.delete(f'model:{request.modelId}')
            pipe.srem(f'user:{request.userId}:models', request.modelId)
            pipe.execute()

        return {
            "status": "success"
        }

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


@router.get("/library")
async def get_library(userId: str):
    """Get the user's library"""
    try:
        client = redis.Redis(host='host.docker.internal', port=6379, decode_responses=True)

        # Get model IDs from the user's set (FAST!)
        model_ids = client.smembers(f'user:{userId}:models')

        # Fetch each model's data
        models = []
        for model_id in model_ids:
            model = client.hgetall(f'model:{model_id}')
            if model:  # Only add if model exists
                models.append(model)

        return models

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

