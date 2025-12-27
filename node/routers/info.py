from fastapi import APIRouter
from utils import get_node_model_status, is_node_authenticated
import state
import app

router = APIRouter(
    prefix="",
    tags=["info"]
)

@router.get("/info")
async def info():
    return {
        "status": "healthy",
        "node_status": get_node_model_status(state.node_id),
        "authenticated": is_node_authenticated(state.node_id),
        "model_loaded": app.currently_active_model_id is not None,
        "active_model": app.currently_active_model_id,
        "loaded_models_count": len(app.loaded_models),
        "device": app.get_device()
    }