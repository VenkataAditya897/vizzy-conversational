from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.routes.deps import get_current_user
from app.models.user import User
from app.services.memory_service import clear_memory
from app.services.memory_service import get_last_memory

router = APIRouter(prefix="/memory", tags=["Memory"])


@router.post("/reset")
def reset_memory(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    clear_memory(db, current_user.id)
    return {"status": "ok", "message": "Memory reset successful"}

@router.get("")
def get_memory(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rows = get_last_memory(db, current_user.id, limit=25)

    return [
        {
            "id": r.id,
            "type": r.memory_type,
            "text": r.text,
            "image_url": r.image_url,
            "created_at": r.created_at
        }
        for r in rows
    ]