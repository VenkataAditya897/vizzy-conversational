import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.conversation_state import ConversationState


def get_state(db: Session, conversation_id: int) -> ConversationState | None:
    return (
        db.query(ConversationState)
        .filter(ConversationState.conversation_id == conversation_id)
        .first()
    )


def set_collecting_state(
    db: Session,
    conversation_id: int,
    draft_prompt: str | None,
    questions: list[str]
) -> ConversationState:
    state = get_state(db, conversation_id)

    questions_json = json.dumps(questions or [])

    if not state:
        state = ConversationState(
            conversation_id=conversation_id,
            status="collecting",
            draft_prompt=draft_prompt,
            pending_questions=questions_json,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(state)
    else:
        state.status = "collecting"
        state.draft_prompt = draft_prompt
        state.pending_questions = questions_json
        state.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(state)
    return state


def clear_state(db: Session, conversation_id: int):
    state = get_state(db, conversation_id)
    if not state:
        return
    db.delete(state)
    db.commit()
