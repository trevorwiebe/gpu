#!/usr/bin/env python3
"""
Simple SmolLM2 Server - Apple Silicon Optimized
FastAPI server that serves SmolLM2-135M-Instruct model
"""

import os
import torch
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from typing import Optional
import uvicorn

# Configuration
MODEL_NAME = "HuggingFaceTB/SmolLM2-135M-Instruct"
MODEL_PATH = os.getenv("MODEL_PATH", f"/models/{MODEL_NAME}")
ROUTER_API_KEY = os.getenv("ROUTER_API_KEY", "secure-router-key-123")

# Pydantic models
class GenerateRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 512
    temperature: float = 0.7
    do_sample: bool = True

class GenerateResponse(BaseModel):
    generated_text: str
    model: str = MODEL_NAME

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
    """Verify API key for all requests except health endpoints"""
    if request.url.path in ["/", "/health", "/docs", "/openapi.json"]:
        response = await call_next(request)
        return response
    
    api_key = request.headers.get("X-API-Key")
    if api_key != ROUTER_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    response = await call_next(request)
    return response

# Global variables for model
tokenizer = None
model = None
generator = None

def get_device():
    """Detect the best available device"""
    if torch.backends.mps.is_available():
        return "mps"
    elif torch.cuda.is_available():
        return "cuda"
    else:
        return "cpu"

def load_model():
    """Load the SmolLM2 model and tokenizer"""
    global tokenizer, model, generator
    
    print(f"Loading model {MODEL_NAME}...")
    print(f"Using device: {get_device()}")
    
    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16 if get_device() != "cpu" else torch.float32,
        device_map="auto" if get_device() != "cpu" else None
    )
    
    # Create generation pipeline
    device = get_device()
    if device == "cpu":
        generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            device=device
        )
    else:
        generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer
        )
    
    print("Model loaded successfully!")

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

@app.post("/generate", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest):
    """Generate text using SmolLM2"""
    if generator is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Generate text
        outputs = generator(
            request.prompt,
            max_new_tokens=request.max_new_tokens,
            temperature=request.temperature,
            do_sample=request.do_sample,
            pad_token_id=tokenizer.eos_token_id,
            return_full_text=False
        )
        
        generated_text = outputs[0]["generated_text"]
        
        return GenerateResponse(generated_text=generated_text)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

if __name__ == "__main__":
    # For local development
    uvicorn.run(app, host="0.0.0.0", port=8005)