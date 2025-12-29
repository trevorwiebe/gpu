#!/usr/bin/env python3

from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import torch #type: ignore
import uuid

import routers.setup as setup
import routers.info as info
import routers.generate as generate
from utils import get_node_api_key

logging.basicConfig(level=logging.INFO)

# Initialize FastAPI app
app = FastAPI(title="Node", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(setup.router)
app.include_router(info.router)
app.include_router(generate.router)

# Global state
loaded_model = {}
node_id = str(uuid.uuid4())

# API Key Authentication Middleware
@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    """Verify API key for all requests except docs and setup endpoints"""
    # Public endpoints - no API key required
    if request.url.path in ["/", "/docs", "/openapi.json"]:
        response = await call_next(request)
        return response

    # Setup endpoints - localhost only, no API key required
    if request.url.path.startswith("/setup"):
        client_host = request.client.host if request.client else None
        logging.info(client_host)
        if client_host not in ["127.0.0.1", "localhost", "::1", "192.168.65.1"]:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Setup endpoints only accessible from localhost"}
            )
        response = await call_next(request)
        return response

    # All other endpoints require API key validation
    api_key = request.headers.get("X-API-Key")
    expected_api_key = get_node_api_key(node_id)

    if not expected_api_key:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Node not authenticated"}
        )

    if api_key != expected_api_key:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid API key"}
        )

    response = await call_next(request)
    return response

def get_device():
    if torch.cuda.is_available() and torch.cuda.device_count() > 0:
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"

if __name__ == "__main__":
    # For local development
    uvicorn.run(app, host="0.0.0.0", port=8005)