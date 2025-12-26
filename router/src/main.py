#!/usr/bin/env python3
"""
Minimal Central Router - HTTP Version
Route requests to nodes via HTTP API
"""

import os
import httpx # type: ignore
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from routers.users.me import library
from routers.users.me import node
from routers import completion

app = FastAPI(title="GPU Router", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(completion.router)
app.include_router(library.router)
app.include_router(node.router)

# Configuration
NODE_URL = os.getenv("NODE_URL", "http://node:8005")
NODE_API_KEY = os.getenv("NODE_API_KEY", "secure-router-key-123")

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