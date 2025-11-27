#!/usr/bin/env python3
"""
Minimal Central Router - HTTP Version
Route requests to nodes via HTTP API
"""

import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="GPU Router", version="1.0.0")

# Configuration
NODE_URL = os.getenv("NODE_URL", "http://node:8005")
NODE_API_KEY = os.getenv("NODE_API_KEY", "secure-router-key-123")

# Pydantic models
class CompletionRequest(BaseModel):
    prompt: str
    model: str = "SmolLM2-135M-Instruct"
    max_tokens: int = 512
    temperature: float = 0.7

class CompletionResponse(BaseModel):
    id: str
    object: str = "text_completion"
    model: str
    choices: list
    usage: dict


@app.post("/completions")
async def completions(request: CompletionRequest):
    """Route completion requests to node"""
    try:
        # Prepare headers with API key
        headers = {"X-API-Key": NODE_API_KEY}
        
        # Prepare request payload for node
        node_request = {
            "prompt": request.prompt,
            "max_new_tokens": request.max_tokens,
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


@app.get("/health")
async def health():
    """Health check"""
    try:
        # Check node health
        headers = {"X-API-Key": NODE_API_KEY}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{NODE_URL}/health",
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code == 200:
                node_health = response.json()
                return {
                    "status": "healthy",
                    "node_status": node_health,
                    "node_url": NODE_URL
                }
            else:
                return {
                    "status": "degraded",
                    "node_status": "unreachable",
                    "node_url": NODE_URL
                }
                
    except Exception as e:
        return {
            "status": "unhealthy",
            "node_status": "error",
            "error": str(e),
            "node_url": NODE_URL
        }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)