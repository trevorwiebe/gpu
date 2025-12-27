
from fastapi import APIRouter, HTTPException
import os
import httpx # type: ignore
import redis

from models.completion import *

NODE_URL = os.getenv("NODE_URL", "http://node:8005")
NODE_API_KEY = os.getenv("NODE_API_KEY", "secure-router-key-123")

router = APIRouter(
    prefix="/completions",
    tags=["completions"]
)

async def find_node_with_model(model_name_or_id: str) -> dict:
    """
    Find a node that has the requested model loaded and ready.

    Returns dict with: nodeId, nodeUrl, modelId, modelName
    Raises HTTPException(404) if model not available
    """
    try:
        client = redis.Redis(host='host.docker.internal', port=6379, decode_responses=True)

        # Strategy 1: Try to find by model ID (exact match)
        model_data = client.hgetall(f'model:{model_name_or_id}')

        if model_data:
            model_id = model_data['modelId']
            model_name = model_data.get('modelName', model_id)
        else:
            # Strategy 2: Search by model name across all models
            model_keys = client.keys('model:*')
            model_id = None
            model_name = None

            for model_key in model_keys:
                data = client.hgetall(model_key)
                if data.get('modelName') == model_name_or_id:
                    model_id = data['modelId']
                    model_name = data['modelName']
                    break

            if not model_id:
                raise HTTPException(
                    status_code=404,
                    detail=f"Model '{model_name_or_id}' not found in library"
                )

        # Find a node with this model loaded and ready
        node_keys = client.keys('node:*')
        node_keys = [k for k in node_keys if not k.endswith(':models')]

        for node_key in node_keys:
            node_id = node_key.replace('node:', '')
            node_data = client.hgetall(node_key)

            if (node_data.get('activeModel') == model_id and
                node_data.get('modelStatus') == 'ready'):

                return {
                    "nodeId": node_id,
                    "nodeUrl": "http://node:8005",  # All nodes on same Docker network
                    "modelId": model_id,
                    "modelName": model_name
                }

        # Model exists but not loaded on any ready node
        raise HTTPException(
            status_code=404,
            detail=f"Model '{model_name_or_id}' is not loaded on any ready node"
        )

    except redis.exceptions.ConnectionError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Redis service unavailable: {str(e)}"
        )
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error finding model: {str(e)}"
        )

@router.post("/")
async def completions(request: CompletionRequest):
    """Route completion requests to node with requested model"""
    try:
        # Find node with the requested model
        node_info = await find_node_with_model(request.model)

        # Prepare headers and request
        headers = {"X-API-Key": NODE_API_KEY}

        # Automatically set do_sample based on temperature (OpenAI-style)
        # temperature=0 means deterministic (greedy), temperature>0 means sampling
        do_sample = request.temperature > 0

        node_request = {
            "prompt": request.prompt,
            "max_new_tokens": request.max_tokens,
            "temperature": request.temperature,
            "do_sample": do_sample
        }

        # Make request to the selected node
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{node_info['nodeUrl']}/generate",
                json=node_request,
                headers=headers,
                timeout=300.0
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Node error: {response.text}"
                )

            node_response = response.json()

            # Convert to OpenAI format
            return {
                "id": f"req_{hash(request.prompt) % 10000}",
                "object": "text_completion",
                "model": node_info['modelName'],  # Use actual model name
                "choices": [{
                    "text": node_response["generated_text"],
                    "index": 0,
                    "finish_reason": "stop"
                }],
                "usage": {
                    "completion_tokens": len(node_response["generated_text"].split()),
                    "prompt_tokens": len(request.prompt.split()),
                    "total_tokens": len(node_response["generated_text"].split()) + len(request.prompt.split())
                }
            }

    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Node unavailable: {str(e)}")
    except HTTPException:
        raise  # Re-raise HTTPExceptions from find_node_with_model
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Router error: {str(e)}")