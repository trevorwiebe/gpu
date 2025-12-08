
from fastapi import APIRouter, HTTPException
import os
import httpx # type: ignore

from models.completion import *

NODE_URL = os.getenv("NODE_URL", "http://node:8005")
NODE_API_KEY = os.getenv("NODE_API_KEY", "secure-router-key-123")

router = APIRouter(
    prefix="/completions",
    tags=["completions"]
)

@router.post("/")
async def completions(request: CompletionRequest):
    """Route completion requests to node"""
    try:
        # Prepare headers with API key
        headers = {"X-API-Key": NODE_API_KEY}
        
        # Prepare request payload for node
        node_request = {
            "prompt": request.prompt,
            "temperature": request.temperature,
            "do_sample": True
        }
        
        # Make request to node
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{NODE_URL}/generate",
                json=node_request,
                headers=headers,
                timeout=60.0
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
                "model": request.model,
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Router error: {str(e)}")