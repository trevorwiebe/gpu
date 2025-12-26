"""
Pydantic models for library endpoints
"""

from pydantic import BaseModel


class SetModelRequest(BaseModel):
    userId: str
    modelId: str
    modelName: str
    isSet: bool
