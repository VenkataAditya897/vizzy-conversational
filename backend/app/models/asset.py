from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)

    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False, index=True)

    type = Column(String, nullable=False) 
    url = Column(String, nullable=False)

    prompt_used = Column(Text, nullable=True)
    model_used = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    message = relationship("Message", back_populates="assets")
