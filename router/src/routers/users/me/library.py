from fastapi import APIRouter, HTTPException
import redis
import uuid

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
            model_uuid = str(uuid.uuid4())

            # Use pipeline to update both the model hash AND the user's set
            pipe = client.pipeline()
            pipe.hset(
                f'model:{model_uuid}',
                mapping={
                    "modelId": model_uuid,
                    "userId": request.userId,
                    "modelName": request.modelName,
                    "huggingFaceModelId": request.modelId
                }
            )
            pipe.sadd(f'user:{request.userId}:models', model_uuid)
            pipe.execute()
        else:
            # Remove from library by looking up the UUID via huggingFaceModelId + userId
            # 1. Get all model UUIDs for this user
            user_models = client.smembers(f'user:{request.userId}:models')

            # 2. Find the UUID that matches the huggingFaceModelId
            target_uuid = None
            for model_uuid in user_models:
                model_data = client.hgetall(f'model:{model_uuid}')
                if model_data.get('huggingFaceModelId') == request.modelId:
                    target_uuid = model_uuid
                    break

            # 3. Delete if found
            if target_uuid:
                pipe = client.pipeline()
                pipe.delete(f'model:{target_uuid}')
                pipe.srem(f'user:{request.userId}:models', target_uuid)
                pipe.execute()
            else:
                raise HTTPException(status_code=404, detail="Model not found in library")

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

        # Get model IDs from the user's set
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

