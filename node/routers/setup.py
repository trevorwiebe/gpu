import uuid
import random
from fastapi import APIRouter, HTTPException
from utils import get_redis_client, is_node_authenticated, get_node_user_id
import state

router = APIRouter(
    prefix="",
    tags=["setup"]
)

def check_authentication_status():
    return is_node_authenticated(state.node_id)
    
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
async def get_setup_info():
    """
    Get setup information for node authentication
    Returns authentication status and setup URL if not authenticated
    """

    if check_authentication_status():
        return {
            "authenticated": True,
            "userId": get_node_user_id(state.node_id),
            "nodeId": state.node_id,
            "message": "Node is already authenticated"
        }

    setup_token = str(uuid.uuid4())
    node_name = generate_node_name()

    try:
        client = get_redis_client()
        client.setex(f'setup_token:{setup_token}', 3600, state.node_id)
        client.setex(f'setup_token_name:{setup_token}', 3600, node_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate setup token: {str(e)}")

    setup_url = f"http://localhost:5173/setup/{setup_token}"
    return {"qrCodeData": setup_url}
