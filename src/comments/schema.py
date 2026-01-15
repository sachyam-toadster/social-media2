from pydantic import BaseModel, Field, field_validator
from typing import Optional
import uuid

class CommentCreate(BaseModel):
    content: str
    parent_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Only provide when replying"
    )

    @field_validator("parent_id", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        return v
