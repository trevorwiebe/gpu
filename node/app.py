#!/usr/bin/env python3
"""
Generic LLM Node Server - GPU Optimized
FastAPI server that serves LLM models with automatic GPU detection
"""

import os
import torch
from fastapi.responses import JSONResponse
import redis
import uuid
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from typing import Optional
import uvicorn
import logging
import random

# Nature-themed word lists for node names
NATURE_ADJECTIVES = [
    "mountain", "forest", "ocean", "river", "meadow", "valley",
    "canyon", "glacier", "coral", "desert", "prairie", "tundra",
    "alpine", "coastal", "highland", "woodland", "wetland", "volcanic"
]

NATURE_NOUNS = [
    "stream", "breeze", "tide", "mist", "bloom", "shadow",
    "light", "dawn", "dusk", "storm", "rain", "snow",
    "wind", "wave", "cloud", "thunder", "frost", "ember"
]

def generate_node_name():
    """Generate a random nature-themed node name"""
    adjective = random.choice(NATURE_ADJECTIVES)
    noun = random.choice(NATURE_NOUNS)
    return f"{adjective}-{noun}"

# Configuration
ROUTER_API_KEY = os.getenv("ROUTER_API_KEY", "secure-router-key-123")
DEVICE_OVERRIDE = os.getenv("DEVICE_OVERRIDE", None)

# Pydantic models
class GenerateRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 512
    temperature: float = 0.7
    do_sample: bool = True

class GenerateResponse(BaseModel):
    generated_text: str
    model: str

class AuthenticateRequest(BaseModel):
    userId: str

class NodeStatusResponse(BaseModel):
    authenticated: bool
    userId: Optional[str] = None
    nodeId: Optional[str] = None

logging.basicConfig(level=logging.INFO)

# Initialize FastAPI app
app = FastAPI(title="SmolLM2 Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key Authentication Middleware
@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    """Verify API key for all requests except health and setup endpoints"""
    # Allow localhost setup endpoints without API key
    if request.url.path in ["/", "/health", "/docs", "/openapi.json", "/setup", "/setup/authenticate", "/setup/status"]:
        # For setup endpoints, only allow localhost
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

    api_key = request.headers.get("X-API-Key")
    if api_key != ROUTER_API_KEY:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid API key"}
        )

    response = await call_next(request)
    return response

# Global variables for model - support for multiple models (future-proofing)
# Structure: { model_id: { "model": obj, "tokenizer": obj, "generator": obj, "model_name": str } }
loaded_models = {}
currently_active_model_id = None  # For single-model mode

# Global variables for node authentication
node_id = str(uuid.uuid4())
node_authenticated = False
node_user_id = None
node_model_status = "idle"  # Values: "idle", "downloading", "loading", "ready", "error"

# Redis connection
def get_redis_client():
    """Get Redis client connection"""
    return redis.Redis(host='host.docker.internal', port=6379, decode_responses=True)

def check_authentication_status():
    """Check if node has been authenticated via Redis"""
    global node_authenticated, node_user_id

    if node_authenticated:
        return True

    try:
        client = get_redis_client()
        node_data = client.hgetall(f'node:{node_id}')

        if node_data and node_data.get('userId'):
            node_authenticated = True
            node_user_id = node_data.get('userId')
            return True

        return False
    except:
        return False

async def poll_for_model_assignments():
    """
    Continuously poll Redis for model assignments
    Only starts polling after node is authenticated
    """
    import asyncio
    global node_authenticated, node_model_status

    POLL_INTERVAL = 5  # seconds

    while True:
        try:
            # Wait until authenticated
            if not check_authentication_status():
                await asyncio.sleep(POLL_INTERVAL)
                continue

            # Check for assigned models in Redis
            client = get_redis_client()
            assigned_model_ids = client.smembers(f'node:{node_id}:models')

            if not assigned_model_ids:
                # No models assigned - unload any loaded models and go idle
                if loaded_models:
                    for model_id in list(loaded_models.keys()):
                        unload_model(model_id)
                    node_model_status = "idle"
                await asyncio.sleep(POLL_INTERVAL)
                continue

            # For single-model support: load first assigned model
            target_model_id = list(assigned_model_ids)[0]

            # Check if we need to load/switch models
            if currently_active_model_id != target_model_id:
                # Get model details from Redis
                model_data = client.hgetall(f'model:{target_model_id}')

                if not model_data:
                    logging.error(f"Model {target_model_id} not found in Redis")
                    await asyncio.sleep(POLL_INTERVAL)
                    continue

                model_name = model_data.get('modelName') or model_data.get('modelId')

                if not model_name:
                    logging.error(f"No model name found for {target_model_id}")
                    await asyncio.sleep(POLL_INTERVAL)
                    continue

                # Unload old models (single-model mode)
                for old_model_id in list(loaded_models.keys()):
                    if old_model_id != target_model_id:
                        unload_model(old_model_id)

                # Load the new model
                success = load_model(target_model_id, model_name)

                # Update node status in Redis
                if success:
                    client.hset(f'node:{node_id}', mapping={
                        "modelStatus": "ready",
                        "activeModel": target_model_id,
                        "activeModelName": model_name
                    })
                else:
                    client.hset(f'node:{node_id}', mapping={
                        "modelStatus": "error",
                        "activeModel": "",
                        "activeModelName": ""
                    })

        except Exception as e:
            logging.error(f"Error in polling loop: {str(e)}")

        await asyncio.sleep(POLL_INTERVAL)

def get_device():
    """Detect the best available device with fallback"""
    if DEVICE_OVERRIDE:
        print(f"Using device override: {DEVICE_OVERRIDE}")
        return DEVICE_OVERRIDE
    
    if torch.cuda.is_available():
        device_count = torch.cuda.device_count()
        if device_count > 0:
            print(f"GPU detected: {device_count} CUDA devices")
            return "cuda"
    
    if torch.backends.mps.is_available():
        print("MPS (Apple Silicon) detected")
        return "mps"
    
    print("No GPU detected, using CPU")
    return "cpu"

def load_model(model_id: str, model_name: str) -> bool:
    """
    Dynamically load a model by downloading it from HuggingFace and loading into memory

    Args:
        model_id: The model ID from Redis (e.g., unique identifier)
        model_name: The HuggingFace model name (e.g., "HuggingFaceTB/SmolLM2-135M-Instruct")

    Returns:
        bool: True if successful, False otherwise
    """
    global loaded_models, currently_active_model_id, node_model_status

    # Check if already loaded
    if model_id in loaded_models:
        logging.info(f"Model {model_id} already loaded")
        currently_active_model_id = model_id
        return True

    try:
        node_model_status = "downloading"
        model_path = f"/models/{model_name}"

        # Download model if not exists
        if not os.path.exists(model_path):
            logging.info(f"Downloading model {model_name} to {model_path}...")
            import subprocess
            result = subprocess.run(
                ["huggingface-cli", "download", model_name, "--local-dir", model_path],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                logging.error(f"Failed to download model: {result.stderr}")
                node_model_status = "error"
                return False

        node_model_status = "loading"
        device = get_device()
        logging.info(f"Loading model {model_name} from {model_path}...")
        logging.info(f"Using device: {device}")

        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name)

        # Load model with device-specific optimizations
        if device == "cuda":
            logging.info("Loading model with CUDA optimizations...")
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True
            )
            generator = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer
            )
        elif device == "mps":
            logging.info("Loading model with MPS optimizations...")
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            generator = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer
            )
        else:
            logging.info("Loading model for CPU...")
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float32
            )
            generator = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                device=device
            )

        # Store in loaded_models dictionary
        loaded_models[model_id] = {
            "model": model,
            "tokenizer": tokenizer,
            "generator": generator,
            "model_name": model_name
        }

        currently_active_model_id = model_id
        node_model_status = "ready"

        logging.info(f"Model {model_name} loaded successfully!")
        logging.info(f"Model device: {model.device}")

        return True

    except Exception as e:
        logging.error(f"Failed to load model {model_name}: {str(e)}")
        node_model_status = "error"
        return False

def unload_model(model_id: str):
    """Unload a model from memory to free resources"""
    global loaded_models, currently_active_model_id

    if model_id in loaded_models:
        logging.info(f"Unloading model {model_id}...")

        # Delete model objects to free memory
        del loaded_models[model_id]

        # Clear CUDA cache if applicable
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        # Update active model if we unloaded it
        if currently_active_model_id == model_id:
            currently_active_model_id = None

        logging.info(f"Model {model_id} unloaded successfully")

@app.on_event("startup")
async def startup_event():
    """Start background polling for model assignments"""
    import asyncio
    asyncio.create_task(poll_for_model_assignments())
    logging.info("Node started in idle mode - waiting for authentication and model assignment")

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "node_status": node_model_status,
        "authenticated": node_authenticated,
        "model_loaded": currently_active_model_id is not None,
        "active_model": currently_active_model_id,
        "device": get_device(),
        "loaded_models_count": len(loaded_models)
    }

@app.get("/device")
async def device_info():
    """Device information endpoint"""
    device = get_device()
    current_device = None
    if currently_active_model_id and currently_active_model_id in loaded_models:
        current_device = str(loaded_models[currently_active_model_id]["model"].device)
    return {
        "device": device,
        "cuda_available": torch.cuda.is_available(),
        "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        "mps_available": torch.backends.mps.is_available(),
        "current_device": current_device,
        "device_override": DEVICE_OVERRIDE
    }

@app.get("/setup")
async def get_setup_info():
    """
    Get setup information for node authentication
    Returns authentication status and setup URL if not authenticated
    """

    # Check if already authenticated
    if check_authentication_status():
        return {
            "authenticated": True,
            "userId": node_user_id,
            "nodeId": node_id,
            "message": "Node is already authenticated"
        }

    # Generate setup token if not exists
    setup_token = str(uuid.uuid4())

    # Generate nature-themed node name
    node_name = generate_node_name()

    try:
        client = get_redis_client()
        # Store setup token in Redis with pending status (expires in 1 hour)
        client.setex(
            f'setup_token:{setup_token}',
            3600,  # 1 hour expiry
            node_id
        )
        # Store node name alongside setup token
        client.setex(
            f'setup_token_name:{setup_token}',
            3600,  # 1 hour expiry
            node_name
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate setup token: {str(e)}"
        )

    # Generate setup URL (adjust domain as needed)
    setup_url = f"http://localhost:5173/setup/{setup_token}"

    return {
        "authenticated": False,
        "nodeId": node_id,
        "nodeName": node_name,
        "setupToken": setup_token,
        "setupUrl": setup_url,
        "message": "Visit the setup URL to authenticate this node",
        "qrCodeData": setup_url  # Frontend can generate QR code from this
    }

@app.post("/generate", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest):
    """Generate text using LLM"""

    # Check if authenticated
    if not node_authenticated:
        raise HTTPException(status_code=403, detail="Node not authenticated")

    # Check if a model is loaded
    if currently_active_model_id is None or currently_active_model_id not in loaded_models:
        raise HTTPException(status_code=503, detail="No model loaded")

    active_model_data = loaded_models[currently_active_model_id]
    generator = active_model_data["generator"]
    tokenizer = active_model_data["tokenizer"]

    try:
        # Generate text
        outputs = generator(
            request.prompt,
            max_new_tokens=request.max_new_tokens,
            temperature=request.temperature,
            do_sample=request.do_sample,
            pad_token_id=tokenizer.eos_token_id if tokenizer else None,
            return_full_text=False
        )

        generated_text = outputs[0]["generated_text"]

        return GenerateResponse(
            generated_text=generated_text,
            model=active_model_data["model_name"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

if __name__ == "__main__":
    # For local development
    uvicorn.run(app, host="0.0.0.0", port=8005)