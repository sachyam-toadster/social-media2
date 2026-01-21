from pydantic import BaseModel
import uuid

class TagUserCreate(BaseModel):
    tagged_user_id: uuid.UUID
