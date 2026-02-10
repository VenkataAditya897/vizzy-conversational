import os
import uuid
import base64
import requests

from openai import OpenAI
from app.config import OPENAI_API_KEY, BASE_URL, IMAGE_MODEL


def transform_image_openai(prompt: str, image_url: str, num_outputs: int, model_name: str | None = None) -> list[str]:
    

    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY missing in .env")

    client = OpenAI(api_key=OPENAI_API_KEY)

    r = requests.get(image_url, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"Could not download input image: {r.status_code}")

    os.makedirs("storage/generated", exist_ok=True)

    tmp_filename = f"{uuid.uuid4().hex}_input.png"
    tmp_path = os.path.join("storage", "generated", tmp_filename)

    with open(tmp_path, "wb") as f:
        f.write(r.content)

    used_model = model_name or IMAGE_MODEL or "gpt-image-1"

    with open(tmp_path, "rb") as img_file:
        resp = client.images.edit(
            model=used_model,
            image=img_file,
            prompt=prompt,
            n=num_outputs,
            size="1024x1024"
        )

    urls = []

    for img in resp.data:
        if not hasattr(img, "b64_json") or not img.b64_json:
            raise RuntimeError("Transform API did not return b64_json")

        img_bytes = base64.b64decode(img.b64_json)

        filename = f"{uuid.uuid4().hex}.png"
        out_path = os.path.join("storage", "generated", filename)

        with open(out_path, "wb") as f:
            f.write(img_bytes)

        urls.append(f"{BASE_URL}/storage/generated/{filename}")

    try:
        os.remove(tmp_path)
    except:
        pass

    return urls
