import json
from app.services.clients.intent_client import get_intent_client
from app.config import INTENT_PROVIDER, INTENT_MODEL
from fastapi import HTTPException
from openai import AuthenticationError, APIConnectionError, RateLimitError


SYSTEM_PROMPT = """
You are an intent classifier for a creative chat application.

Your job:
- Decide whether output should be IMAGE or VIDEO.
- Decide whether this is GENERATE or TRANSFORM.
- Decide how many outputs to generate.

Rules:
1) If the user provides an image, mode MUST be "transform" unless the user clearly says "ignore the image".
2) If user asks for video, animation, reel, loop, gif-like, cinematic loop, product loop => output_type MUST be "video".
3) If only image is provided and no text => output_type MUST be "image" and mode MUST be "transform".
4) This system is one-shot: DO NOT ask follow-up questions.
5) Always return STRICT JSON ONLY. No markdown. No explanation.
6) If the user_text is not a creative request (examples: "hi", "hello", "how are you", "ok", "hmm", random words)
   then return:
   {
     "output_type": "invalid",
     "mode": "generate",
     "task": "generic",
     "num_outputs": 1,
     "aspect_ratio": "1:1",
     "video_seconds": null,
     "error_message": "Please write a proper creative prompt. Example: 'Make a premium poster for a coffee brand'."
   }

Allowed output JSON schema:

{
  "output_type": "image" | "video" | "invalid",
  "mode": "generate" | "transform",
  "task": "poster" | "moodboard" | "product_shot" | "portrait" | "artwork" | "story_scene" | "signage" | "generic",
  "num_outputs": 1 | 2 | 3 | 4,
  "aspect_ratio": "1:1" | "16:9" | "9:16" | "4:5",
  "video_seconds": 5 | 6 | 7 | 8 | 9 | 10 | null
}

Return JSON that is always valid.
"""


def classify_intent(
    *,
    user_text: str | None,
    image_url: str | None,
    memory_prompts: list[str]
) -> dict:
   

    memory_block = ""
    if memory_prompts:
        ordered = list(reversed(memory_prompts))
        memory_block = "\n".join([f"{i+1}. {p}" for i, p in enumerate(ordered)])

    user_text_clean = user_text.strip() if user_text else ""

    user_prompt = f"""
INPUTS:
- user_text: {json.dumps(user_text_clean)}
- image_url_present: {bool(image_url)}

USER_MEMORY_LAST_25_PROMPTS:
{memory_block if memory_block else "(none)"}

TASK:
Return the classification JSON.
"""

    client = get_intent_client()
    model_name = INTENT_MODEL


    try:
        resp = client.chat.completions.create(
            model=model_name,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT.strip()},
                {"role": "user", "content": user_prompt.strip()},
            ],
        )
    except AuthenticationError:
        # wrong key / missing key
        return {
            "output_type": "invalid",
            "mode": "generate",
            "task": "generic",
            "num_outputs": 1,
            "aspect_ratio": "1:1",
            "video_seconds": None,
            "error_message": "OpenAI API key is missing or invalid. Please add a valid OPENAI_API_KEY in backend/.env and restart the server."
        }
    except RateLimitError:
        return {
            "output_type": "invalid",
            "mode": "generate",
            "task": "generic",
            "num_outputs": 1,
            "aspect_ratio": "1:1",
            "video_seconds": None,
            "error_message": "Rate limit hit. Please try again in a minute."
        }
    except APIConnectionError:
        return {
            "output_type": "invalid",
            "mode": "generate",
            "task": "generic",
            "num_outputs": 1,
            "aspect_ratio": "1:1",
            "video_seconds": None,
            "error_message": "Cannot connect to OpenAI. Check your internet connection."
        }
    except Exception as e:
        return {
            "output_type": "invalid",
            "mode": "generate",
            "task": "generic",
            "num_outputs": 1,
            "aspect_ratio": "1:1",
            "video_seconds": None,
            "error_message": f"Intent classifier failed: {str(e)}"
        }




    raw = resp.choices[0].message.content.strip()

    try:
        data = json.loads(raw)
    except Exception:
        raise ValueError(f"Classifier returned invalid JSON: {raw}")
    if data.get("output_type") == "image":
        data["video_seconds"] = None

    if data.get("output_type") == "video" and data.get("video_seconds") is None:
        data["video_seconds"] = 5


    required_keys = {"output_type", "mode", "task", "num_outputs", "aspect_ratio", "video_seconds"}

    if "error_message" not in data:
        data["error_message"] = None
    if not required_keys.issubset(set(data.keys())):
        raise ValueError(f"Classifier JSON missing keys. Got: {data}")

    if data["output_type"] not in ["image", "video", "invalid"]:

        raise ValueError(f"Invalid output_type: {data['output_type']}")

    if data["mode"] not in ["generate", "transform"]:
        raise ValueError(f"Invalid mode: {data['mode']}")

    if data["num_outputs"] not in [1, 2, 3, 4]:
        raise ValueError(f"Invalid num_outputs: {data['num_outputs']}")

    if data["aspect_ratio"] not in ["1:1", "16:9", "9:16", "4:5"]:
        raise ValueError(f"Invalid aspect_ratio: {data['aspect_ratio']}")

   
    if data["output_type"] == "video":
        if data["video_seconds"] not in [5, 6, 7, 8, 9, 10]:
            raise ValueError("video_seconds must be 5-10 for video output")

    elif data["output_type"] == "invalid":
        if not data.get("error_message"):
            data["error_message"] = "Please write a proper creative prompt."
        return data

    else:
        if data["video_seconds"] is not None:
            raise ValueError("video_seconds must be null for image output")

    return data
