"""
Pydantic models for model endpoints
"""

from pydantic import BaseModel

class Model(BaseModel):
    modelId: str