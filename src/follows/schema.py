from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime

class FollowUserResponse(BaseModel):
    message: str
    follower_id: UUID
    following_id: UUID
    is_following: bool

class FollowerResponse(BaseModel):
    username: str
    first_name: str
    last_name: str

    class Config:
        from_attributes = True   # IMPORTANT for ORM