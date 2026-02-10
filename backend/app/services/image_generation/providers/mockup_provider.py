import os
import random
from app.config import BASE_URL

MOCKUP_IMAGES_DIR = os.path.join("mockups", "images")

ALLOWED_EXT = (".png", ".jpg", ".jpeg", ".webp")


def generate_images(prompt: str, num_outputs: int, aspect_ratio: str, model_name: str = "mockup") -> list[str]:
    if not os.path.exists(MOCKUP_IMAGES_DIR):
        raise RuntimeError(f"Mockup images folder not found: {MOCKUP_IMAGES_DIR}")

    files = [
        f for f in os.listdir(MOCKUP_IMAGES_DIR)
        if f.lower().endswith(ALLOWED_EXT)
    ]

    if not files:
        raise RuntimeError("No mockup images found in mockups/images/")

    urls = []
    for _ in range(num_outputs):
        chosen = random.choice(files)
        urls.append(f"{BASE_URL}/mockups/images/{chosen}")

    return urls
