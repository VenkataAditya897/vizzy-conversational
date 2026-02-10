# Vizzy Chat 🎬✨

A creative chat application that automatically decides whether the user wants an **image** or a **video**, then generates it using AI.

This project is built like a real product:

- **FastAPI backend**
- **SQLite DB**
- **JWT Auth**
- **Memory (last 25 prompts FIFO)**
- **Intent classifier (1 API call only)**
- **Image generation + Image transform**
- **Video generation + Video from image**
- **Clean minimal frontend UI (HTML/CSS/JS)**

---

## ✅ Features

### 🔐 Authentication

- Signup + Login
- JWT-based authentication
- Token stored in localStorage

### 💬 Conversations

- Create new chats
- View old chats
- Messages stored in DB

### 🧠 Preferences Memory (FIFO)

- Stores the last **25 prompts**
- FIFO queue: newest kept, oldest removed
- Can be turned ON/OFF in UI
- Reset button clears memory

### 🧠 Intent Classifier (Only 1 API call)

The backend uses an LLM intent classifier that returns strict JSON like:

```json
{
  "output_type": "image",
  "mode": "transform",
  "task": "poster",
  "num_outputs": 4,
  "aspect_ratio": "1:1",
  "video_seconds": null
}
```

Rules:

- **No fallback**
- If classifier returns invalid JSON → request fails
- If prompt is invalid (“hi”, “ok”) → returns `output_type="invalid"` and raises 400

### 🖼️ Image Generation

- Text → Image
- Image + Text → Transform

Provider:

- OpenAI (`gpt-image-1`)

### 🎥 Video Generation

- Text → Video
- Image + Text → Video

Provider:

- OpenAI Sora (`sora-2`)

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

## 🚀 Setup (Local Run)

### 1) Clone the repo

```bash
git clone https://github.com/VenkataAditya897/vizzy-chat.git
cd vizzy-chat
```

### 2) Create virtual environment

```bash
cd backend
python -m venv venv
venv\Scripts\activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Setup `.env`

Create a file:

`backend/.env`

Example:

```env
DATABASE_URL=sqlite:///./vizzy.db
JWT_SECRET=secret
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080

OPENAI_API_KEY=your_openai_key_here
GROQ_API_KEY=your_groq_key_here

BASE_URL=http://127.0.0.1:8000

# INTENT CLASSIFIER
INTENT_PROVIDER=groq
INTENT_MODEL=llama-3.3-70b-versatile

# IMAGE GENERATION
IMAGE_PROVIDER=openai
IMAGE_MODEL=gpt-image-1

# VIDEO GENERATION
VIDEO_PROVIDER=openai
VIDEO_MODEL=sora-2
```

⚠️ Important:

- `GROQ_API_KEY` is required if `INTENT_PROVIDER=groq`
- `OPENAI_API_KEY` is required for image/video generation

---

## ▶️ Run Backend

From inside the `backend/` folder:

```bash
uvicorn app.main:app --reload
```

Backend runs on:

- http://127.0.0.1:8000/

Frontend is served automatically at:

- http://127.0.0.1:8000/

---

## 🖥️ Using the App

1. Open: `http://127.0.0.1:8000/`
2. Signup / Login
3. Create chat
4. Type prompt OR upload image
5. Click **Send**
6. App automatically decides image/video

---

## 🧠 Memory Logic (FIFO last 25)

- Memory is stored in `user_memory` table
- When `use_preferences=true`, the user’s prompt is saved
- After insert, the DB is trimmed to keep only latest 25

---

## 🌍 Deployment

This project is deployed on Render:

- Live URL: https://vizzy-chat.onrender.com/

---

## 📌 GitHub Repo

- Repo: https://github.com/VenkataAditya897/vizzy-chat

---

## 👤 Author

**Venkata Aditya Gopalapuram**  
GitHub: https://github.com/VenkataAditya897
