from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class PendingRequest(BaseModel):
    model: str
    query: str

class FullfilledRequest(BaseModel):
    result: str

@app.post("/v1/completions", response_model=FullfilledRequest)
async def create_completion(request: PendingRequest):
    new_result = FullfilledRequest(
        result=request.query
    )
    return new_result