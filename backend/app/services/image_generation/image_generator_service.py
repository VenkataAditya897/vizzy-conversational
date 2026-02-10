from app.config import IMAGE_PROVIDER, IMAGE_MODEL
from app.services.image_generation.providers import openai_provider
from app.services.image_generation.providers import mockup_provider
from app.services.generators.openai_transform import transform_image_openai


def generate_images(prompt: str, num_outputs: int, aspect_ratio: str) -> tuple[list[str], str]:
    if IMAGE_PROVIDER == "openai":
        urls = openai_provider.generate_images(
            prompt=prompt,
            num_outputs=num_outputs,
            aspect_ratio=aspect_ratio,
            model_name=IMAGE_MODEL
        )
        return urls, f"openai-{IMAGE_MODEL}"

    if IMAGE_PROVIDER == "mockup":
        urls = mockup_provider.generate_images(
            prompt=prompt,
            num_outputs=num_outputs,
            aspect_ratio=aspect_ratio,
            model_name="mockup"
        )
        return urls, "mockup-image"

    raise RuntimeError(f"Unknown IMAGE_PROVIDER: {IMAGE_PROVIDER}")


def transform_images(prompt: str, image_url: str, num_outputs: int) -> tuple[list[str], str]:
    if IMAGE_PROVIDER == "openai":
        urls = transform_image_openai(
            prompt=prompt,
            image_url=image_url,
            num_outputs=num_outputs,
            model_name=IMAGE_MODEL
        )
        return urls, f"openai-{IMAGE_MODEL}"

    if IMAGE_PROVIDER == "mockup":
        # even transform just returns mock images
        urls = mockup_provider.generate_images(
            prompt=prompt,
            num_outputs=num_outputs,
            aspect_ratio="1:1",
            model_name="mockup"
        )
        return urls, "mockup-transform"

    raise RuntimeError(f"Unknown IMAGE_PROVIDER: {IMAGE_PROVIDER}")
