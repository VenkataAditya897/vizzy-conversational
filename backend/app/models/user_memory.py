from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime
from app.db import Base


class UserMemory(Base):
    __tablename__ = "user_memory"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True, index=True)

    memory_type = Column(String, nullable=False)

    text = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
