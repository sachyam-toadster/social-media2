from datetime import datetime
import uuid
from typing import List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func
import sqlalchemy.dialects.postgresql as pg


class User(SQLModel, table=True):
    __tablename__ = "user_accounts"

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            unique=True,
            nullable=False,
            default=uuid.uuid4,
            info={"description": "Unique identifier for the user account"},
        )
    )

    username: str
    first_name: str = Field(nullable=True)
    last_name: str = Field(nullable=True)
    role: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="user")) 
    is_verified: bool = False
    email: str
    password_hash: str
    preferred_language: str = Field(sa_column=Column(pg.VARCHAR, server_default="en"))
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False))
    update_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    def __repr__(self) -> str:
        return f"<User {self.username}>"
    

