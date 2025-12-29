import os
import httpx # type: ignore
from fastapi import APIRouter

# Configuration
NODE_URL = os.getenv("NODE_URL", "http://node:8005")
NODE_API_KEY = os.getenv("NODE_API_KEY", "secure-router-key-123")

router = APIRouter(
    prefix="",
    tags=["health"]
)

@router.get("/health")
async def health():
    """Health check"""
    try:
        # Check node health
        headers = {"X-API-Key": NODE_API_KEY}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{NODE_URL}/health",
                headers=headers,
                timeout=10.0
            )
            node_health = response.json()
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "node_repsonse": node_health,
                    "node_url": NODE_URL
                }
            else:
                return {
                    "status": "degraded",
                    "node_response": node_health,
                    "node_url": NODE_URL
                }
                
    except Exception as e:
        return {
            "status": "unhealthy",
            "node_status": "error",
            "error": str(e),
            "node_url": NODE_URL
        }
