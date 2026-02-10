from pydantic import BaseModel
from typing import Optional, List


class GenerationInput(BaseModel):
    prompt: str
    num_outputs: int = 1
    aspect_ratio: str = "1:1"
    image_url: Optional[str] = None


class GeneratedAsset(BaseModel):
    type: str 
    url: str
    prompt_used: str
    model_used: str


class GenerationResult(BaseModel):
    assets: List[GeneratedAsset]
