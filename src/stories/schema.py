from pydantic import BaseModel
import uuid
from datetime import datetime

class StoryCreate(BaseModel):
    media_url: str
    media_type: str

class StoryRead(BaseModel):
    id: uuid.UUID
    media_url: str
    media_type: str
    created_at: datetime
    expires_at: datetime

class StoryViewerOut(BaseModel):
    user_id: uuid.UUID
    username: str
