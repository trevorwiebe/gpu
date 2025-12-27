#!/usr/bin/env python3

import os
import torch
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import uvicorn
import logging

import routers.setup as setup
from utils import get_redis_client, update_node_status_in_redis, is_node_authenticated, get_node_model_status
import state

from models.models import GenerateRequest, GenerateResponse

# Configuration
ROUTER_API_KEY = os.getenv("ROUTER_API_KEY", "secure-router-key-123")
DEVICE_OVERRIDE = os.getenv("DEVICE_OVERRIDE", None)

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

async def poll_for_model_assignments():
    """
    Continuously poll Redis for model assignments
    Only starts polling after node is authenticated
    """
    import asyncio

    POLL_INTERVAL = 5  # seconds

    while True:
        try:
            # Wait until authenticated
            if not is_node_authenticated(state.node_id):
                await asyncio.sleep(POLL_INTERVAL)
                continue

            # Check for assigned models in Redis
            client = get_redis_client()
            assigned_model_ids = client.smembers(f'node:{state.node_id}:models')

            if not assigned_model_ids:
                # No models assigned - unload any loaded models and go idle
                if loaded_models:
                    for model_id in list(loaded_models.keys()):
                        unload_model(model_id)
                    update_node_status_in_redis(state.node_id, "idle")
                currently_active_model_id = None
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

                # Update node status in Redis (redundant but ensures consistency)
                if success:
                    update_node_status_in_redis(state.node_id, "ready", target_model_id, model_name)
                else:
                    update_node_status_in_redis(state.node_id, "error", "", "")
                    # Mark as attempted to prevent infinite retry loop
                    # Will only retry if model is unassigned then reassigned
                    currently_active_model_id = target_model_id

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
    global loaded_models, currently_active_model_id

    # Check if already loaded
    if model_id in loaded_models:
        logging.info(f"Model {model_id} already loaded")
        currently_active_model_id = model_id
        return True

    try:
        update_node_status_in_redis(state.node_id, "downloading", model_id, model_name)
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
                update_node_status_in_redis(state.node_id, "error", "", "")
                return False

        update_node_status_in_redis(state.node_id, "loading", model_id, model_name)
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
                dtype=torch.float16,
                low_cpu_mem_usage=True,
                device_map="auto"
            )
            generator = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer
            )

        # Store in loaded_models dictionary
        loaded_models[model_id] = {
            "model": model,
            "tokenizer": tokenizer,
            "generator": generator,
            "model_name": model_name
        }

        currently_active_model_id = model_id
        update_node_status_in_redis(state.node_id, "ready", model_id, model_name)

        logging.info(f"Model {model_name} loaded successfully!")
        logging.info(f"Model device: {model.device}")

        return True

    except Exception as e:
        logging.error(f"Failed to load model {model_name}: {str(e)}")
        update_node_status_in_redis(state.node_id, "error", "", "")
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
    return {
        "status": "healthy",
        "node_status": get_node_model_status(state.node_id),
        "authenticated": is_node_authenticated(state.node_id),
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

@app.post("/generate", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest):
    if not is_node_authenticated(state.node_id):
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