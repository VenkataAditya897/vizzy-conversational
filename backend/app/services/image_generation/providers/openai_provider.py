import os
import uuid
import base64

from openai import OpenAI
from app.config import OPENAI_API_KEY, BASE_URL


def _aspect_to_size(aspect: str) -> str:
    if aspect == "1:1":
        return "1024x1024"
    if aspect == "16:9":
        return "1792x1024"
    if aspect == "9:16":
        return "1024x1792"
    if aspect == "4:5":
        return "1024x1280"
    return "1024x1024"


def generate_images(prompt: str, num_outputs: int, aspect_ratio: str, model_name: str) -> list[str]:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY missing in .env")

    client = OpenAI(api_key=OPENAI_API_KEY)

    size = _aspect_to_size(aspect_ratio)

    resp = client.images.generate(
        model=model_name,
        prompt=prompt,
        size=size,
        n=num_outputs
    )

    urls = []
    os.makedirs("storage/generated", exist_ok=True)

    for img in resp.data:
        if not hasattr(img, "b64_json") or not img.b64_json:
            raise RuntimeError("OpenAI did not return b64_json")

        img_bytes = base64.b64decode(img.b64_json)

        filename = f"{uuid.uuid4().hex}.png"
        out_path = os.path.join("storage", "generated", filename)

        with open(out_path, "wb") as f:
            f.write(img_bytes)

        urls.append(f"{BASE_URL}/storage/generated/{filename}")

    return urls
