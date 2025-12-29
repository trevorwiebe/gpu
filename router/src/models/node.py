"""
Pydantic models for node endpoints
"""

from pydantic import BaseModel
from typing import Optional

class Node(BaseModel):
    nodeId: str
    ownerId: str

class AuthenticateNodeRequest(BaseModel):
    setupToken: str
    userId: str

class AssignModelToNodeRequest(BaseModel):
    userId: str
    nodeId: str
    modelId: str
    modelName: Optional[str] = None
    huggingFaceModelId: Optional[str] = None