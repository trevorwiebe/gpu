
from pydantic import BaseModel
from typing import Optional

# Pydantic models
class CompletionRequest(BaseModel):
    prompt: str
    model: str
    temperature: Optional[float] = 1.0
    max_tokens: Optional[int] = 4096

class CompletionResponse(BaseModel):
    id: str
    object: str
    model: str
    choices: list
    usage: dict