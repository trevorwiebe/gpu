"""
Pydantic models for node endpoints
"""

from pydantic import BaseModel

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