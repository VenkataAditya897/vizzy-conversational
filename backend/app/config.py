import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vizzy.db")

JWT_SECRET = os.getenv("JWT_SECRET", "secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "10080"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

PLANNER_PROVIDER = os.getenv("PLANNER_PROVIDER", "groq")
PLANNER_MODEL = os.getenv("PLANNER_MODEL", "llama-3.3-70b-versatile")

VISION_PLANNER_PROVIDER = os.getenv("VISION_PLANNER_PROVIDER", "openai")
VISION_PLANNER_MODEL = os.getenv("VISION_PLANNER_MODEL", "gpt-4o-mini")

IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "openai")
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "gpt-image-1")


BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")

