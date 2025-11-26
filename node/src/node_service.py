#!/usr/bin/env python3
"""
Minimal GPU Node Service - Prototype Version
Just the absolute basics: connect, receive requests, process, send back
"""

import os
import asyncio
import json
from vllm import AsyncLLMEngine, SamplingParams
from vllm.engine.arg_utils import AsyncEngineArgs
import websockets

# Config
HUB_URL = os.getenv("HUB_URL", "ws://localhost:8000/ws")
NODE_ID = os.getenv("NODE_ID", "node_test_123")
MODEL_PATH = os.getenv("MODEL_PATH", "/models/llama-3.1-8b")

class SimpleNode:
    def __init__(self):
        self.node_id = NODE_ID
        self.engine = None
        self.ws = None
    
    async def start(self):
        """Load model and connect"""
        print(f"Loading model from {MODEL_PATH}...")
        
        # Initialize vLLM
        engine_args = AsyncEngineArgs(
            model=MODEL_PATH,
            dtype="auto",
            max_model_len=4096,
        )
        self.engine = AsyncLLMEngine.from_engine_args(engine_args)
        print("Model loaded!")
        
        # Connect to hub
        print(f"Connecting to {HUB_URL}...")
        async with websockets.connect(HUB_URL) as ws:
            self.ws = ws
            
            # Register
            await ws.send(json.dumps({
                "type": "register",
                "node_id": self.node_id,
                "model": "llama-3.1-8b"
            }))
            print("Connected and registered!")
            
            # Listen for requests
            async for message in ws:
                msg = json.loads(message)
                
                if msg["type"] == "inference_request":
                    asyncio.create_task(self.process_request(msg))
    
    async def process_request(self, msg):
        """Process a single request"""
        request_id = msg["request_id"]
        prompt = msg["prompt"]
        params = msg.get("parameters", {})
        
        print(f"Processing request {request_id}")
        
        # Generate with vLLM
        sampling_params = SamplingParams(
            temperature=params.get("temperature", 0.7),
            max_tokens=params.get("max_tokens", 512),
        )
        
        result = await self.engine.generate(prompt, sampling_params, request_id)
        output_text = result.outputs[0].text
        
        # Send response back
        await self.ws.send(json.dumps({
            "type": "inference_response",
            "request_id": request_id,
            "output": output_text,
            "tokens": len(result.outputs[0].token_ids)
        }))
        
        print(f"Completed request {request_id}")


if __name__ == "__main__":
    node = SimpleNode()
    asyncio.run(node.start())