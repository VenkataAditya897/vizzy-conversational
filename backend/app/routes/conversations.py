from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.asset import Asset
from app.routes.deps import get_current_user
from app.models.user import User
from app.routes.schemas import (
    ConversationCreateRequest,
    ConversationResponse,
    ConversationDetailResponse,
    MessageWithAssetsResponse,
    AssetResponse
)

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.post("", response_model=ConversationResponse)
def create_conversation(
    payload: ConversationCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    title = payload.title or "New Chat"

    convo = Conversation(user_id=current_user.id, title=title)
    db.add(convo)
    db.commit()
    db.refresh(convo)

    return convo


@router.get("", response_model=List[ConversationResponse])
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    convos = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.created_at.desc())
        .all()
    )
    return convos


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    convo = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
        .first()
    )

    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages_out = []

    for msg in convo.messages:
        assets_out = [
            AssetResponse(
                id=a.id,
                type=a.type,
                url=a.url,
                prompt_used=a.prompt_used,
                model_used=a.model_used,
                created_at=a.created_at
            )
            for a in msg.assets
        ]

        messages_out.append(
            MessageWithAssetsResponse(
                id=msg.id,
                role=msg.role,
                text=msg.text,
                created_at=msg.created_at,
                assets=assets_out
            )
        )

    return ConversationDetailResponse(
        id=convo.id,
        title=convo.title,
        created_at=convo.created_at,
        messages=messages_out
    )

@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    convo = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
        .first()
    )

    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")

    db.delete(convo)
    db.commit()

    return {"status": "ok", "message": "Conversation deleted"}
