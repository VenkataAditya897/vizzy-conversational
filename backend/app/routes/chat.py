from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.services.memory_service import add_memory_row
from app.services.intent_classifier import classify_intent
from app.services.memory_service import get_last_memory
from app.services.image_generation.image_generator_service import generate_images, transform_images
from app.services.video_generation.video_generator_service import (
    generate_video,
    generate_video_from_image
)

from app.db import get_db
from app.routes.deps import get_current_user
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.asset import Asset

from app.routes.schemas import (
    ChatSendRequest,
    ChatSendResponse,
    MessageWithAssetsResponse,
    AssetResponse
)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/send", response_model=ChatSendResponse)
def chat_send(
    payload: ChatSendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    convo = None

    if payload.conversation_id:
        convo = (
            db.query(Conversation)
            .filter(
                Conversation.id == payload.conversation_id,
                Conversation.user_id == current_user.id
            )
            .first()
        )
        if not convo:
            raise HTTPException(status_code=404, detail="Conversation not found")


    memory_prompts = []
    if payload.use_preferences:
        rows = get_last_memory(db, current_user.id, limit=25)
        for r in rows:
            if r.text and r.text.strip():
                memory_prompts.append(r.text.strip())


    intent = classify_intent(
        user_text=payload.text,
        image_url=payload.image_url,
        memory_prompts=memory_prompts
    )

    if intent["output_type"] == "invalid":
        raise HTTPException(
            status_code=400,
            detail=intent.get("error_message") or "Invalid prompt"
        )


    if not convo:
        title = "New Chat"
        if payload.text and payload.text.strip():
            title = payload.text.strip()[:40]

        convo = Conversation(user_id=current_user.id, title=title)
        db.add(convo)
        db.commit()
        db.refresh(convo)

    user_msg = Message(
        conversation_id=convo.id,
        role="user",
        text=payload.text
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)
    
    if payload.use_preferences:
        if payload.text and payload.text.strip():
            add_memory_row(
                db=db,
                user_id=current_user.id,
                conversation_id=convo.id,
                memory_type="text",
                text=payload.text.strip(),
                image_url=None
            )
        elif payload.image_url:
            add_memory_row(
                db=db,
                user_id=current_user.id,
                conversation_id=convo.id,
                memory_type="image",
                text=None,
                image_url=payload.image_url
            )

    final_prompt = ""

    if payload.use_preferences and memory_prompts:
        memory_text = "\n".join([f"- {p}" for p in memory_prompts])
        final_prompt = f"""
    User taste history (last 25 prompts):
    {memory_text}

    Now generate based on this new request:
    {payload.text or "No text provided. Use taste + image."}
    """.strip()
    else:
        final_prompt = (payload.text or "").strip()

    if not final_prompt and payload.image_url and not payload.use_preferences:
        raise HTTPException(
            status_code=400,
            detail="No text + preferences OFF. Cannot decide transform style."
        )

    generated_urls = []
    model_used = ""

    if intent["output_type"] == "image":

        if intent["mode"] == "generate":
            generated_urls, model_used = generate_images(
                prompt=final_prompt,
                num_outputs=intent["num_outputs"],
                aspect_ratio=intent["aspect_ratio"]
            )

        elif intent["mode"] == "transform":
            if not payload.image_url:
                raise HTTPException(status_code=400, detail="Transform mode requires image_url")

            generated_urls, model_used = transform_images(
                prompt=final_prompt,
                image_url=payload.image_url,
                num_outputs=intent["num_outputs"]
            )

        else:
            raise HTTPException(status_code=400, detail="Invalid mode")

    
    else:
        seconds = intent.get("video_seconds") or 5

        if payload.image_url:
            generated_urls, model_used = generate_video_from_image(
                prompt=final_prompt,
                image_url=payload.image_url,
                seconds=seconds
            )
        else:
            generated_urls, model_used = generate_video(
                prompt=final_prompt,
                seconds=seconds
            )




    
    assistant_msg = Message(
        conversation_id=convo.id,
        role="assistant",
        text="Generated successfully."
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    saved_assets = []
    asset_type = "video" if intent["output_type"] == "video" else "image"


    for url in generated_urls:
        asset = Asset(
            message_id=assistant_msg.id,
            type=asset_type,
            url=url,
            prompt_used=final_prompt,
            model_used=model_used
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)
        saved_assets.append(asset)


    user_out = MessageWithAssetsResponse(
        id=user_msg.id,
        role=user_msg.role,
        text=user_msg.text,
        created_at=user_msg.created_at,
        assets=[]
    )

    assistant_out = MessageWithAssetsResponse(
        id=assistant_msg.id,
        role=assistant_msg.role,
        text=assistant_msg.text,
        created_at=assistant_msg.created_at,
        assets=[
            AssetResponse(
                id=a.id,
                type=a.type,
                url=a.url,
                prompt_used=a.prompt_used,
                model_used=a.model_used,
                created_at=a.created_at
            )
            for a in saved_assets
        ]
    )


    return ChatSendResponse(
        conversation_id=convo.id,
        intent=intent,
        user_message=user_out,
        assistant_message=assistant_out
    )

