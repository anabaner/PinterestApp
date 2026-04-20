from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PinCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    image_url: str
    tags: Optional[str] = ""
    board: Optional[str] = "General"

class PinUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    board: Optional[str] = None

class PinResponse(BaseModel):
    id: int
    title: str
    description: str
    image_url: str
    tags: str
    board: str
    created_at: datetime

    class Config:
        from_attributes = True