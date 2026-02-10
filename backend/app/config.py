import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vizzy.db")

JWT_SECRET = os.getenv("JWT_SECRET", "secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "10080"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

INTENT_PROVIDER = os.getenv("INTENT_PROVIDER", "groq")
INTENT_MODEL = os.getenv("INTENT_MODEL", "llama-3.3-70b-versatile")

IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "openai")
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "gpt-image-1")

VIDEO_PROVIDER = os.getenv("VIDEO_PROVIDER", "openai")
VIDEO_MODEL = os.getenv("VIDEO_MODEL", "sora-2")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "")
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")

