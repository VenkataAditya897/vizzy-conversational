from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    title = Column(String, nullable=False, default="New Chat")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    messages = relationship("Message", back_populates="conversation", cascade="all, delete")
