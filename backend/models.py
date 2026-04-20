from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class Pin(Base):
    __tablename__ = "pins"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String, nullable=False)
    description = Column(String, default="")
    image_url   = Column(String, nullable=False)
    tags        = Column(String, default="")
    board       = Column(String, default="General")
    created_at  = Column(DateTime, server_default=func.now())