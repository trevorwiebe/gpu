import uuid
import random
import asyncio
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from utils import get_redis_client, is_node_authenticated, get_node_user_id, update_node_status_in_redis
import logging
import os
import torch #type: ignore
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

import app
from models.models import AssignModel

router = APIRouter(
    prefix="",
    tags=["setup"]
)
    
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

@router.get("/setup")
async def get_setup_info(request: Request):
    """
    Get setup information for node authentication
    Returns authentication status and setup URL if not authenticated
    """

    if is_node_authenticated(app.node_id):
        return {
            "authenticated": True,
            "userId": get_node_user_id(app.node_id),
            "nodeId": app.node_id,
            "message": "Node is already authenticated"
        }

    public_ip = os.getenv("PUBLIC_IPADDR")
    port = os.getenv("EXTERNAL_PORT")
    router_ip = os.getenv("ROUTER_PUBLIC_IPADDR")
    if not public_ip:
        raise HTTPException(status_code=500, detail="PUBLIC_IPADDR environment variable is not set")
    if not port:
        raise HTTPException(status_code=500, detail="EXTERNAL_PORT environment variable is not set")
    if not router_ip:
        raise HTTPException(status_code=500, detail="ROUTER_PUBLIC_IPADDR environment variable is not set")
    
    setup_token = str(uuid.uuid4())
    node_name = generate_node_name()
    node_url = f"http://{public_ip}:{port}"

    try:
        client = get_redis_client()
        client.setex(f'setup_token:{setup_token}', 3600, app.node_id)
        client.setex(f'setup_token_name:{setup_token}', 3600, node_name)
        client.setex(f'setup_node_url:{setup_token}', 3600, node_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate setup token: {str(e)}")

    setup_url = f"http://{router_ip}/setup/{setup_token}"
    return {"qrCodeData": setup_url}

@router.post("/assign-model")
async def post_assign_model(request: AssignModel):
    """
    Used to assign or replace a model on the node
    """

    # Make sure we have the node we think we do
    if not request.nodeId == app.node_id:
        raise HTTPException(
            status_code=404,
            detail="Node not found with that id."
        )

    # Check if the node is authenticated
    if not is_node_authenticated(request.nodeId):
        raise HTTPException(
            status_code=401,
            detail="This node is not authenticated.  Please authenticate by calling http://localhost:PORT/setup."
        )

    client = get_redis_client()
    node = client.hgetall(f'node:{request.nodeId}')

    if node.get('activeModelId'):
        if app.loaded_model.get('model_id') == request.modelId:
            return JSONResponse(
                content={"detail": f"{request.modelId} is currently loaded"},
                status_code=208
            )
        else:
            unload_model(request.modelId)

    # Set initial status in Redis
    update_node_status_in_redis(app.node_id, "queued", request.modelId, request.modelName)

    # Start the model loading in the background
    asyncio.create_task(load_model_async(request.modelId, request.modelName))

    # Return immediately with 202 Accepted
    return JSONResponse(
        content={
            "detail": f"Model {request.modelId} loading started.",
            "status": "queued"
        },
        status_code=202
    )

async def load_model_async(model_id: str, model_name: str):
    """Async wrapper for load_model to run in background"""
    await asyncio.to_thread(load_model, model_id, model_name)

def load_model(
        model_id: str,
        model_name: str
    ) -> bool:

    try:
        update_node_status_in_redis(app.node_id, "downloading", model_id, model_name)
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
                update_node_status_in_redis(app.node_id, "error", "", "")
                return False

        update_node_status_in_redis(app.node_id, "loading", model_id, model_name)
        device = app.get_device()
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
        app.loaded_model = {
            "model": model,
            "tokenizer": tokenizer,
            "generator": generator,
            "model_name": model_name,
            "model_id": model_id
        }

        update_node_status_in_redis(app.node_id, "ready", model_id, model_name)

        logging.info(f"Model {model_name} loaded successfully!")
        logging.info(f"Model device: {model.device}")

        return True

    except Exception as e:
        logging.error(f"Failed to load model {model_name}: {str(e)}")
        update_node_status_in_redis(app.node_id, "error", "", "")
        return False
    
def unload_model(new_model_id: str):
    """Unload a model from memory to free resources"""

    logging.info(f"Unloading model {new_model_id}...")

    app.loaded_model = {}

    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    logging.info(f'Model {new_model_id} unloaded successfully')  

