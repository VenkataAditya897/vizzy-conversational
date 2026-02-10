from pydantic import BaseModel, EmailStr

from typing import Optional, List
from datetime import datetime
class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: EmailStr

class ConversationCreateRequest(BaseModel):
    title: Optional[str] = None


class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime


class MessageResponse(BaseModel):
    id: int
    role: str
    text: Optional[str]
    created_at: datetime


class AssetResponse(BaseModel):
    id: int
    type: str
    url: str
    prompt_used: Optional[str]
    model_used: Optional[str]
    created_at: datetime


class MessageWithAssetsResponse(BaseModel):
    id: int
    role: str
    text: Optional[str]
    created_at: datetime
    assets: List[AssetResponse] = []


class ConversationDetailResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    messages: List[MessageWithAssetsResponse] = []

class ChatSendRequest(BaseModel):
    conversation_id: Optional[int] = None
    text: Optional[str] = None
    image_url: Optional[str] = None
    use_preferences: bool = True


class IntentResponse(BaseModel):
    output_type: str
    mode: str
    task: str
    num_outputs: int
    aspect_ratio: str
    video_seconds: Optional[int] = None
    error_message: Optional[str] = None



class ChatSendResponse(BaseModel):
    conversation_id: int
    intent: IntentResponse
    user_message: MessageWithAssetsResponse
    assistant_message: MessageWithAssetsResponse
