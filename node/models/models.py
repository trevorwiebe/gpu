from pydantic import BaseModel
from typing import Optional

# Pydantic models
class GenerateRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 512
    temperature: float = 0.7
    do_sample: bool = True

class GenerateResponse(BaseModel):
    generated_text: str
    model: str

class AuthenticateRequest(BaseModel):
    userId: str

class NodeStatusResponse(BaseModel):
    authenticated: bool
    userId: Optional[str] = None
    nodeId: Optional[str] = None