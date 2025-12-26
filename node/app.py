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
MODEL_NAME = os.getenv("MODEL_NAME", "HuggingFaceTB/SmolLM2-135M-Instruct")
MODEL_PATH = os.getenv("MODEL_PATH", f"/models/{MODEL_NAME}")
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
    model: str = MODEL_NAME

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

# Global variables for model
tokenizer = None
model = None
generator = None

# Global variables for node authentication
node_id = str(uuid.uuid4())
node_authenticated = False
node_user_id = None

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

def load_model():
    """Load the LLM model and tokenizer with device optimization"""
    global tokenizer, model, generator
    
    device = get_device()
    print(f"Loading model {MODEL_NAME}...")
    print(f"Using device: {device}")
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    
    # Load model with device-specific optimizations
    if device == "cuda":
        print("Loading model with CUDA optimizations...")
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
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
        print("Loading model with MPS optimizations...")
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer
        )
    else:
        print("Loading model for CPU...")
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float32
        )
        generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            device=device
        )
    
    print("Model loaded successfully!")
    print(f"Model device: {model.device}")

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    load_model()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SmolLM2 Server",
        "model": MODEL_NAME,
        "device": get_device(),
        "status": "ready"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model": MODEL_NAME,
        "device": get_device(),
        "model_loaded": generator is not None
    }

@app.get("/device")
async def device_info():
    """Device information endpoint"""
    device = get_device()
    return {
        "device": device,
        "cuda_available": torch.cuda.is_available(),
        "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        "mps_available": torch.backends.mps.is_available(),
        "current_device": str(model.device) if model else None,
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
    if generator is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
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
        
        return GenerateResponse(generated_text=generated_text)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

if __name__ == "__main__":
    # For local development
    uvicorn.run(app, host="0.0.0.0", port=8005)