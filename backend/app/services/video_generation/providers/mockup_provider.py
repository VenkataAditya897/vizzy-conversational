import os
import random
from app.config import BASE_URL

MOCKUP_VIDEOS_DIR = os.path.join("mockups", "videos")

ALLOWED_EXT = (".mp4",)


def generate_video(prompt: str, seconds: int, model_name: str = "mockup") -> list[str]:
    if not os.path.exists(MOCKUP_VIDEOS_DIR):
        raise RuntimeError(f"Mockup videos folder not found: {MOCKUP_VIDEOS_DIR}")

    files = [
        f for f in os.listdir(MOCKUP_VIDEOS_DIR)
        if f.lower().endswith(ALLOWED_EXT)
    ]

    if not files:
        raise RuntimeError("No mockup videos found in mockups/videos/")

    chosen = random.choice(files)
    return [f"{BASE_URL}/mockups/videos/{chosen}"]


def generate_video_from_image(prompt: str, image_url: str, seconds: int, model_name: str = "mockup") -> list[str]:
    # Same logic: just return a random mockup mp4
    return generate_video(prompt=prompt, seconds=seconds, model_name=model_name)
