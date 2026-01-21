from pydantic import BaseModel, conlist, model_validator, constr
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from enum import Enum

class MediaType(str, Enum):
    image = "image"
    video = "video"

class MediaCreate(BaseModel):
    media_url: constr(strip_whitespace=True, min_length=1)
    media_type: MediaType
    media_order: int
    

class PostCreate(BaseModel):
    caption: Optional[str] = None
    media: conlist(MediaCreate, min_length=1)
    is_reel: bool = False

    @model_validator(mode="after")
    def validate_reel(self):
        if self.is_reel:
            if len(self.media) != 1:
                raise ValueError("Reel must contain exactly one media")

            if self.media[0].media_type != "video":
                raise ValueError("Reel media must be of type 'video'")

        return self

class PostRead(BaseModel):
    id: UUID
    user_id: UUID
    caption: Optional[str]
    media_url: str
    is_reel: bool
    created_at: datetime

    class Config:
        from_attributes = True
