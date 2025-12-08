
from pydantic import BaseModel

# Pydantic models
class CompletionRequest(BaseModel):
    prompt: str
    model: str = "SmolLM2-135M-Instruct"
    temperature: float = 0.7

class CompletionResponse(BaseModel):
    id: str
    object: str = "text_completion"
    model: str
    choices: list
    usage: dict