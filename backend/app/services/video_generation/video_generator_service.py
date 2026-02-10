from app.config import VIDEO_PROVIDER, VIDEO_MODEL
from app.services.video_generation.providers import openai_sora_provider
from app.services.video_generation.providers import mockup_provider


def generate_video(prompt: str, seconds: int) -> tuple[list[str], str]:
    if VIDEO_PROVIDER == "openai":
        urls = openai_sora_provider.generate_video(
            prompt=prompt,
            seconds=seconds,
            model_name=VIDEO_MODEL
        )
        return urls, f"openai-{VIDEO_MODEL}"

    if VIDEO_PROVIDER == "mockup":
        urls = mockup_provider.generate_video(
            prompt=prompt,
            seconds=seconds,
            model_name="mockup"
        )
        return urls, "mockup-video"

    raise RuntimeError(f"Unknown VIDEO_PROVIDER: {VIDEO_PROVIDER}")


def generate_video_from_image(prompt: str, image_url: str, seconds: int) -> tuple[list[str], str]:
    if VIDEO_PROVIDER == "openai":
        urls = openai_sora_provider.generate_video_from_image(
            prompt=prompt,
            image_url=image_url,
            seconds=seconds,
            model_name=VIDEO_MODEL
        )
        return urls, f"openai-{VIDEO_MODEL}"

    if VIDEO_PROVIDER == "mockup":
        urls = mockup_provider.generate_video_from_image(
            prompt=prompt,
            image_url=image_url,
            seconds=seconds,
            model_name="mockup"
        )
        return urls, "mockup-video-from-image"

    raise RuntimeError(f"Unknown VIDEO_PROVIDER: {VIDEO_PROVIDER}")
