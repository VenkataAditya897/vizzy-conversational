from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
from app.services.memory_service import get_last_memory, format_memory_for_prompt
from app.services.vision_planner_service import run_vision_planner

from app.services.memory_service import add_memory_row

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

from app.services.image_generation.image_generator_service import generate_images, transform_images
from app.services.history_service import get_conversation_history
from app.services.planner_service import run_planner
from app.services.conversation_state_service import (
    get_state,
    set_collecting_state,
    clear_state
)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/send", response_model=ChatSendResponse)
def chat_send(
    payload: ChatSendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ----------------------------
    # Step 1: Load / Create conversation
    # ----------------------------
    convo = None
    preferences_memory_text = None

    if payload.use_preferences:
        rows = get_last_memory(db, current_user.id, limit=25)
        preferences_memory_text = format_memory_for_prompt(rows)


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

    if not convo:
        title = "New Chat"
        if payload.text and payload.text.strip():
            title = payload.text.strip()[:40]

        convo = Conversation(user_id=current_user.id, title=title)
        db.add(convo)
        db.commit()
        db.refresh(convo)

    # ----------------------------
    # Step 2: Save user message
    # ----------------------------
    user_text = (payload.text or "").strip()

    if not user_text and not payload.image_url:
        raise HTTPException(status_code=400, detail="Please type something or upload an image.")

    user_msg = Message(
        conversation_id=convo.id,
        role="user",
        text=payload.text
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)
    # Save user prompt into memory (FIFO) only if enabled
    

    # ----------------------------
    # Step 3: Load state + history
    # ----------------------------
    state = get_state(db, convo.id)

    draft_prompt = state.draft_prompt if state else None
    pending_questions = []

    if state and state.pending_questions:
        try:
            pending_questions = json.loads(state.pending_questions)
        except:
            pending_questions = []

    history = get_conversation_history(db, convo.id, limit=20)

    # ----------------------------
    # Step 4: Call Groq planner
    # ----------------------------
    try:
        # If user uploaded an image -> use Vision planner (OpenAI)
        if payload.image_url:
            planner = run_vision_planner(
                user_message=user_text,
                image_url=payload.image_url,
                history=history,
                draft_prompt=draft_prompt,
                pending_questions=pending_questions,
                preferences_memory=preferences_memory_text
            )
        else:
            planner = run_planner(
                user_message=user_text,
                history=history,
                draft_prompt=draft_prompt,
                pending_questions=pending_questions,
                preferences_memory=preferences_memory_text
            )


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # ----------------------------
    # Case A: Planner asks questions
    # ----------------------------
    if planner["type"] == "question":
        questions = (planner.get("questions") or [])[:1]

        if not questions:
            questions = ["What would you like to generate?"]

        assistant_text = questions[0]


        assistant_msg = Message(
            conversation_id=convo.id,
            role="assistant",
            text=assistant_text
        )
        db.add(assistant_msg)
        db.commit()
        db.refresh(assistant_msg)

        # Save collecting state
        set_collecting_state(
            db,
            conversation_id=convo.id,
            draft_prompt=planner.get("draft_prompt") or draft_prompt or user_text,
            questions=questions
        )

        return ChatSendResponse(
            conversation_id=convo.id,
            user_message=MessageWithAssetsResponse(
                id=user_msg.id,
                role=user_msg.role,
                text=user_msg.text,
                created_at=user_msg.created_at,
                assets=[]
            ),
            assistant_message=MessageWithAssetsResponse(
                id=assistant_msg.id,
                role=assistant_msg.role,
                text=assistant_msg.text,
                created_at=assistant_msg.created_at,
                assets=[]
            )
        )

    # ----------------------------
    # Case B: Planner returns final prompt
    # ----------------------------
    if planner["type"] != "final":
        raise HTTPException(status_code=500, detail=f"Planner returned invalid type: {planner.get('type')}")

    final_prompt = planner["final_prompt"]
    # Save final prompt into preferences memory (only if enabled)
    if payload.use_preferences and final_prompt:
        add_memory_row(
            db=db,
            user_id=current_user.id,
            conversation_id=convo.id,
            memory_type="text",
            text=final_prompt
        )

    num_outputs = planner.get("num_outputs", 4)
    aspect_ratio = planner.get("aspect_ratio", "1:1")

    # IMPORTANT: Clear state now
    clear_state(db, convo.id)

    # ----------------------------
    # Step 5: Generate images
    # ----------------------------
    try:
        if payload.image_url:
            generated_urls, model_used = transform_images(
                prompt=final_prompt,
                image_url=payload.image_url,
                num_outputs=num_outputs
            )
        else:
            generated_urls, model_used = generate_images(
                prompt=final_prompt,
                num_outputs=num_outputs,
                aspect_ratio=aspect_ratio
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

    # ----------------------------
    # Step 6: Save assistant message (store final prompt!)
    # ----------------------------
    assistant_msg = Message(
        conversation_id=convo.id,
        role="assistant",
        text=final_prompt
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    # ----------------------------
    # Step 7: Save assets
    # ----------------------------
    saved_assets = []

    for url in generated_urls:
        asset = Asset(
            message_id=assistant_msg.id,
            type="image",
            url=url,
            prompt_used=final_prompt,
            model_used=model_used
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)
        saved_assets.append(asset)

    # ----------------------------
    # Step 8: Return response
    # ----------------------------
    return ChatSendResponse(
        conversation_id=convo.id,
        user_message=MessageWithAssetsResponse(
            id=user_msg.id,
            role=user_msg.role,
            text=user_msg.text,
            created_at=user_msg.created_at,
            assets=[]
        ),
        assistant_message=MessageWithAssetsResponse(
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
    )
