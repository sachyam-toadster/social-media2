from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from enum import Enum

class MediaType(str, Enum):
    image = "image"
    video = "video"

class MediaCreate(BaseModel):
    media_url: str
    media_type: MediaType
    media_order: int
    

class PostCreate(BaseModel):
    caption: Optional[str] = None
    media: List[MediaCreate]
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
