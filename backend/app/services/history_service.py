from sqlalchemy.orm import Session
from app.models.message import Message


def get_conversation_history(db: Session, conversation_id: int, limit: int = 12) -> list[dict]:
    msgs = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )

    msgs = msgs[-limit:]

    out = []
    for m in msgs:
        if not m.text:
            continue
        out.append({"role": m.role, "content": m.text})
    return out
