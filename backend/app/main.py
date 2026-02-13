from fastapi import FastAPI
from app.db import Base, engine
from app.models import User, Conversation, Message, Asset, UserMemory, ConversationState
from app.routes.memory import router as memory_router
from fastapi.middleware.cors import CORSMiddleware
from app.routes.upload import router as upload_router

from app.routes.auth import router as auth_router
from app.routes.conversations import router as conversations_router
from app.routes.chat import router as chat_router
from fastapi.staticfiles import StaticFiles
import os
from fastapi.responses import FileResponse


app = FastAPI(title="Vizzy Chat API", version="0.0.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(conversations_router)
app.include_router(chat_router)
app.include_router(memory_router)
app.include_router(upload_router)
os.makedirs("storage/generated", exist_ok=True)
os.makedirs("storage/tmp", exist_ok=True)

app.mount("/storage", StaticFiles(directory="storage"), name="storage")
app.mount("/mockups", StaticFiles(directory="mockups"), name="mockups")


FRONTEND_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))

app.mount("/frontend", StaticFiles(directory=FRONTEND_PATH), name="frontend")
@app.get("/app")
def serve_app():
    return FileResponse(os.path.join(FRONTEND_PATH, "index.html"))

@app.get("/")
def root():
    return FileResponse(os.path.join(FRONTEND_PATH, "index.html"))
