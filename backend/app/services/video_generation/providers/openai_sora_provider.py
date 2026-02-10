import os
import uuid
import time
import requests

from openai import OpenAI
from app.config import OPENAI_API_KEY, BASE_URL


def _aspect_to_size(aspect: str) -> str:
    if aspect == "16:9":
        return "1280x720"
    if aspect == "9:16":
        return "720x1280"
    return "1280x720"


def generate_video(prompt: str, seconds: int, model_name: str) -> list[str]:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY missing in .env")

    client = OpenAI(api_key=OPENAI_API_KEY)

    video = client.videos.create(
        model=model_name,
        prompt=prompt,
        seconds=str(seconds),
        size="1280x720"
    )

    while video.status in ["queued", "in_progress"]:
        time.sleep(4)
        video = client.videos.retrieve(video.id)

    if video.status != "completed":
        raise RuntimeError(f"Video generation failed. Status={video.status}")

    content = client.videos.download_content(video.id)

    mp4_bytes = content.read()


    os.makedirs("storage/generated", exist_ok=True)

    filename = f"{uuid.uuid4().hex}.mp4"
    out_path = os.path.join("storage", "generated", filename)

    with open(out_path, "wb") as f:
        f.write(mp4_bytes)

    return [f"{BASE_URL}/storage/generated/{filename}"]


def generate_video_from_image(prompt: str, image_url: str, seconds: int, model_name: str) -> list[str]:
    
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY missing in .env")

    client = OpenAI(api_key=OPENAI_API_KEY)

    r = requests.get(image_url, timeout=30)
    if r.status_code != 200:
        raise RuntimeError("Could not download reference image")

    os.makedirs("storage/tmp", exist_ok=True)

    tmp_file = os.path.join("storage", "tmp", f"{uuid.uuid4().hex}.png")
    with open(tmp_file, "wb") as f:
        f.write(r.content)

    with open(tmp_file, "rb") as ref_img:
        video = client.videos.create(
            model=model_name,
            prompt=prompt,
            seconds=str(seconds),
            size="1280x720",
            input_reference=ref_img
        )

    while video.status in ["queued", "in_progress"]:
        time.sleep(4)
        video = client.videos.retrieve(video.id)

    if video.status != "completed":
        raise RuntimeError(f"Video generation failed. Status={video.status}")

    content = client.videos.download_content(video.id)

    mp4_bytes = content.read()


    os.makedirs("storage/generated", exist_ok=True)

    filename = f"{uuid.uuid4().hex}.mp4"
    out_path = os.path.join("storage", "generated", filename)

    with open(out_path, "wb") as f:
        f.write(mp4_bytes)

    try:
        os.remove(tmp_file)
    except:
        pass

    return [f"{BASE_URL}/storage/generated/{filename}"]
