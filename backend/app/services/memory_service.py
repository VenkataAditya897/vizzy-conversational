from sqlalchemy.orm import Session
from app.models.user_memory import UserMemory


MAX_MEMORY = 25


def add_memory_row(
    db: Session,
    user_id: int,
    conversation_id: int | None,
    memory_type: str,
    text: str | None = None,
    image_url: str | None = None
):
    row = UserMemory(
        user_id=user_id,
        conversation_id=conversation_id,
        memory_type=memory_type,
        text=text,
        image_url=image_url
    )

    db.add(row)
    db.commit()
    db.refresh(row)

    trim_memory(db, user_id)

    return row


def trim_memory(db: Session, user_id: int):
    rows = (
        db.query(UserMemory)
        .filter(UserMemory.user_id == user_id)
        .order_by(UserMemory.created_at.desc())
        .all()
    )

    if len(rows) <= MAX_MEMORY:
        return

    to_delete = rows[MAX_MEMORY:]

    for r in to_delete:
        db.delete(r)

    db.commit()


def clear_memory(db: Session, user_id: int):
    db.query(UserMemory).filter(UserMemory.user_id == user_id).delete()
    db.commit()


def get_last_memory(db: Session, user_id: int, limit: int = 25):
    return (
        db.query(UserMemory)
        .filter(UserMemory.user_id == user_id)
        .order_by(UserMemory.created_at.desc())
        .limit(limit)
        .all()
    )
