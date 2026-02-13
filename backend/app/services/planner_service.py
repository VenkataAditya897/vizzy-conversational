import json
from groq import Groq
from app.config import GROQ_API_KEY, PLANNER_MODEL


SYSTEM_PROMPT = """
You are a creative planning assistant for an AI image generator.

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

IMPORTANT RULES:
- Confirmation must be understood naturally (NO keyword matching).
- If the user gives a clear subject + setting, you may output type="final" even without explicit confirmation.
- Ask a question ONLY if something is truly unclear.
- When asking a question, be friendly, playful, include emojis and keep it interactive (but keep it short).


FINAL PROMPT QUALITY RULES:
When type="final", you MUST produce a highly detailed, cinematic, creative, high-quality generative prompt.
It should include:
- subject description
- environment
- lighting
- mood
- camera angle / composition
- style keywords
Make it descriptive and vivid, but natural.
DO NOT mention resolution (4k/8k), camera specs, or aspect ratio in the final prompt.

Make it feel like a premium Midjourney-style prompt.

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




def run_planner(
    user_message: str,
    history: list[dict],
    draft_prompt: str | None = None,
    pending_questions: list[str] | None = None,
    preferences_memory: str | None = None
) -> dict:
    

    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY missing in .env")

    client = Groq(api_key=GROQ_API_KEY)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

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

    messages.append({"role": "user", "content": user_message})


    resp = client.chat.completions.create(
        model=PLANNER_MODEL,
        messages=messages,
        temperature=0.2,
    )

    raw = resp.choices[0].message.content.strip()

    try:
        data = json.loads(raw)
    except Exception:
        raise RuntimeError(f"Planner returned invalid JSON:\n{raw}")

    if "type" not in data:
        raise RuntimeError(f"Planner JSON missing type:\n{raw}")

    if data["type"] == "question":
        data["final_prompt"] = None
        data["questions"] = (data.get("questions") or [])[:1]

    if data["type"] == "final":
        if not data.get("final_prompt"):
            raise RuntimeError(f"Planner returned final without final_prompt:\n{raw}")
        data["questions"] = []

    data["num_outputs"] = int(data.get("num_outputs") or 4)
    data["aspect_ratio"] = data.get("aspect_ratio") or "1:1"

    return data
