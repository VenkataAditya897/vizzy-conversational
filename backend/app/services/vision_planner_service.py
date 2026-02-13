import json
from openai import OpenAI
from app.config import OPENAI_API_KEY, VISION_PLANNER_MODEL


VISION_SYSTEM_PROMPT = """
You are a creative planning assistant for an AI image generator.

You can SEE the uploaded image.

You must output STRICT JSON only.

You must decide:
1) Ask ONLY 1 question at a time
OR
2) Return a FINAL prompt ready for image generation

You will be given:
- Conversation history
- Optional existing draft prompt
- Optional pending questions
- Optional user preferences memory (last 25)
- Latest user message
- An image (vision input)

IMPORTANT RULES:
- Confirmation must be understood naturally (NO keyword matching).
- Ask a question ONLY if something is truly unclear.
- If user says "looks good", "continue", "generate", etc → treat it as confirmation naturally.

FINAL PROMPT QUALITY RULES:
When type="final", produce a highly detailed cinematic prompt.
Include:
- subject
- environment
- lighting
- mood
- composition
- style keywords
DO NOT mention resolution.

Return JSON format:
{
  "type": "question" | "final",
  "questions": ["..."],
  "final_prompt": "string or null",
  "draft_prompt": "string or null",
  "num_outputs": 4,
  "aspect_ratio": "1:1"
}
"""


def run_vision_planner(
    user_message: str,
    image_url: str,
    history: list[dict],
    draft_prompt: str | None = None,
    pending_questions: list[str] | None = None,
    preferences_memory: str | None = None
) -> dict:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY missing in .env")

    client = OpenAI(api_key=OPENAI_API_KEY)

    messages = [{"role": "system", "content": VISION_SYSTEM_PROMPT}]

    if preferences_memory:
        messages.append({
            "role": "system",
            "content": f"User preferences memory (last 25):\n{preferences_memory}"
        })

    if draft_prompt:
        messages.append({"role": "system", "content": f"Current draft prompt:\n{draft_prompt}"})

    if pending_questions:
        messages.append({"role": "system", "content": f"Pending questions previously asked:\n{pending_questions}"})

    if history:
        messages.extend(history[-20:])

    messages.append({
        "role": "user",
        "content": [
            {"type": "text", "text": user_message or "User uploaded an image."},
            {"type": "image_url", "image_url": {"url": image_url}}
        ]
    })

    resp = client.chat.completions.create(
        model=VISION_PLANNER_MODEL,
        messages=messages,
        temperature=0.2,
        response_format={"type": "json_object"}
    )

    raw = resp.choices[0].message.content.strip()

    try:
        data = json.loads(raw)
    except Exception:
        raise RuntimeError(f"Vision planner returned invalid JSON:\n{raw}")

    if "type" not in data:
        raise RuntimeError(f"Vision planner JSON missing type:\n{raw}")

    if data["type"] == "question":
        data["final_prompt"] = None
        data["questions"] = (data.get("questions") or [])[:1]

    if data["type"] == "final":
        if not data.get("final_prompt"):
            raise RuntimeError(f"Vision planner returned final without final_prompt:\n{raw}")
        data["questions"] = []

    data["num_outputs"] = int(data.get("num_outputs") or 4)
    data["aspect_ratio"] = data.get("aspect_ratio") or "1:1"

    return data
