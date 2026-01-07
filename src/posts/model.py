from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

class Post(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    caption: Optional[str] = None
    media_url: str
    is_reel: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
