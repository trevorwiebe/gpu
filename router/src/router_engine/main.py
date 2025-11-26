#!/usr/bin/env python3
"""
Minimal Central Router - Prototype Version
Just route requests to nodes, that's it
"""

import asyncio
import json
from typing import Dict
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

# Simple in-memory storage
nodes: Dict[str, WebSocket] = {}  # node_id -> websocket
pending_requests: Dict[str, asyncio.Future] = {}  # request_id -> future
request_counter = 0


@app.websocket("/ws")
async def node_websocket(websocket: WebSocket):
    """Nodes connect here"""
    await websocket.accept()
    node_id = None
    
    try:
        # Wait for registration
        data = await websocket.receive_json()
        node_id = data["node_id"]
        nodes[node_id] = websocket
        print(f"Node {node_id} connected")
        
        # Listen for responses
        while True:
            msg = await websocket.receive_json()
            
            if msg["type"] == "inference_response":
                request_id = msg["request_id"]
                if request_id in pending_requests:
                    pending_requests[request_id].set_result(msg)
                    
    except Exception as e:
        print(f"Node {node_id} disconnected: {e}")
    finally:
        if node_id in nodes:
            del nodes[node_id]


@app.post("/v1/completions")
async def completions(request: dict):
    """Clients send requests here"""
    global request_counter
    
    if not nodes:
        return JSONResponse({"error": "No nodes available"}, status_code=503)
    
    # Pick first available node (no fancy routing)
    node_id = list(nodes.keys())[0]
    node_ws = nodes[node_id]
    
    # Create request
    request_counter += 1
    request_id = f"req_{request_counter}"
    
    # Create future to wait for response
    future = asyncio.Future()
    pending_requests[request_id] = future
    
    # Send to node
    await node_ws.send_json({
        "type": "inference_request",
        "request_id": request_id,
        "prompt": request["prompt"],
        "parameters": {
            "temperature": request.get("temperature", 0.7),
            "max_tokens": request.get("max_tokens", 512),
        }
    })
    
    # Wait for response (with timeout)
    try:
        response = await asyncio.wait_for(future, timeout=60)
        del pending_requests[request_id]
        
        return {
            "id": request_id,
            "object": "text_completion",
            "model": request.get("model", "llama-3.1-8b"),
            "choices": [{
                "text": response["output"],
                "index": 0,
                "finish_reason": "stop"
            }],
            "usage": {
                "completion_tokens": response.get("tokens", 0),
                "total_tokens": response.get("tokens", 0)
            }
        }
        
    except asyncio.TimeoutError:
        del pending_requests[request_id]
        return JSONResponse({"error": "Request timeout"}, status_code=504)


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "nodes_connected": len(nodes)
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)