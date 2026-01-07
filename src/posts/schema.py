from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class PostCreate(BaseModel):
    caption: Optional[str] = None
    media_url: str
    is_reel: bool = False

class PostRead(BaseModel):
    id: UUID
    user_id: UUID
    caption: Optional[str]
    media_url: str
    is_reel: bool
    created_at: datetime

    class Config:
        from_attributes = True
