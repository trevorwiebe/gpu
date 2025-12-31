from fastapi import APIRouter, HTTPException
from utils import is_node_authenticated
import app

from models.models import GenerateRequest, GenerateResponse

router = APIRouter(
    prefix="",
    tags=["generate"]
)

@router.post("/generate", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest):
    if not is_node_authenticated(app.node_id):
        raise HTTPException(status_code=403, detail="Node not authenticated")

    # Check if a model is loaded
    if not app.loaded_model:
        raise HTTPException(status_code=503, detail="No model loaded")

    active_model_data = app.loaded_model
    generator = active_model_data["generator"]
    tokenizer = active_model_data["tokenizer"]

    try:
        # Generate text
        outputs = generator(
            request.prompt,
            max_new_tokens=request.max_new_tokens,
            temperature=request.temperature,
            do_sample=request.do_sample,
            pad_token_id=tokenizer.eos_token_id if tokenizer else None,
            return_full_text=False
        )

        generated_text = outputs[0]["generated_text"]

        return GenerateResponse(
            generated_text=generated_text,
            model=active_model_data["model_name"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")