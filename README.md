# Vizzy Conversational 🎨💬

A **conversational AI image studio** where the assistant **asks smart questions**, waits for natural confirmation, then generates **4 high‑quality images** — with full chat history, assets, and memory saved.

---

## ✨ Features

### 💬 Conversational Planner (LLM)

The assistant returns **strict JSON**:

- `type = "question"` → asks **only 1 question at a time**
- `type = "final"` → returns the final prompt

No hardcoded confirmation keywords.  
The LLM understands confirmation naturally.

---

### 🧠 Conversation State (DB)

A `conversation_state` table tracks:

- whether we are still collecting info
- the current `draft_prompt`
- pending questions

This makes the “confirm → generate” flow reliable.

---

### 🖼️ Image Generation

Supports:

- Text → Image generation
- Image + Text → Transform (edit)

Providers:

- **OpenAI** (`gpt-image-1`)
- **Mockup provider** (random local images for UI testing)

---

### 👁️ Vision Planner (Auto)

When the user uploads/selects an image:

- planner automatically switches from Groq → **OpenAI Vision**
- the model can understand the image
- then returns the same strict JSON

---

### 🖱️ Click-to-Edit Images

Users can click any generated image in chat:

- it becomes the selected input image
- next prompt will edit/transform that image

---

### 🧠 Preferences Memory (FIFO last 25)

Optional memory system:

- stores last 25 final prompts
- FIFO queue
- can be turned ON/OFF in UI
- reset button clears memory

---

## 📂 Project Structure

```
AIP/
  backend/
    app/
      main.py
      config.py
      db.py
      models/
      routes/
      services/
    storage/
      generated/
      tmp/
    mockups/
      images/
    requirements.txt
    .env
  frontend/
    index.html
    app.js
    styles.css
```

---

## ⚙️ Requirements

- Python **3.10+**
- pip

---

## 🚀 Local Setup

### 1) Create virtual environment

```bash
cd backend
python -m venv venv
venv\Scripts\activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Create `.env`

Create:

`backend/.env`

Example:

```env
DATABASE_URL=sqlite:///./vizzy.db

JWT_SECRET=secret
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080

BASE_URL=http://127.0.0.1:8000

OPENAI_API_KEY=your_openai_key_here
GROQ_API_KEY=your_groq_key_here

# Text-only planner (fast)
PLANNER_PROVIDER=groq
PLANNER_MODEL=llama-3.3-70b-versatile

# Image planner (vision)
VISION_PLANNER_PROVIDER=openai
VISION_PLANNER_MODEL=gpt-4o-mini

# Image generation provider
IMAGE_PROVIDER=openai
IMAGE_MODEL=gpt-image-1
```

---

## ▶️ Run Backend

From inside `backend/`:

```bash
uvicorn app.main:app --reload
```

Backend runs on:

- http://127.0.0.1:8000/

Frontend is served automatically at:

- http://127.0.0.1:8000/

---

## 🧪 Mockup Mode (for UI testing)

Put some images in:

```
backend/mockups/images/
```

Then set:

```env
IMAGE_PROVIDER=mockup
```

Restart backend and you will get random local mockups.

---

## ✅ How the System Works

### User clicks Send

1. Save user message in DB
2. Choose planner:
   - Text only → Groq planner
   - Image present → OpenAI Vision planner
3. Planner returns:
   - 1 question (max)
   - OR a final prompt
4. If final prompt:
   - generate 4 images
   - save assets in DB
   - render in UI

---

## 👤 Author

**Venkata Aditya Gopalapuram**  
GitHub: https://github.com/VenkataAditya897
