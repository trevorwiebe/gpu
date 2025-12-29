from fastapi import APIRouter
from utils import is_node_authenticated, get_node_details
import app

router = APIRouter(
    prefix="",
    tags=["info"]
)

@router.get("/info")
async def info():

    node_details = get_node_details(app.node_id)

    return {
        "node_name": node_details.get('nodeName'),
        "node_status": node_details.get('status'),
        "active_model_name": node_details.get('activeModelName'),
        "active_model_id": node_details.get('activeModelId'),
        "model_status": node_details.get('modelStatus'),
        "authenticated": is_node_authenticated(app.node_id),
        "device": app.get_device()
    }