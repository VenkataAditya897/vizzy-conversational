from openai import OpenAI
from groq import Groq
from app.config import GROQ_API_KEY, OPENAI_API_KEY, INTENT_PROVIDER

def get_intent_client():
    if INTENT_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY missing")
        return OpenAI(api_key=OPENAI_API_KEY)

    if INTENT_PROVIDER == "groq":
        if not GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY missing")
        return Groq(api_key=GROQ_API_KEY)

    raise RuntimeError(f"Unknown INTENT_PROVIDER: {INTENT_PROVIDER}")
