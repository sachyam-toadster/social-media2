from datetime import datetime
import uuid
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func, UniqueConstraint
import sqlalchemy.dialects.postgresql as pg


class User(SQLModel, table=True):
    __tablename__ = "user_accounts"

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            nullable=False,
            default=uuid.uuid4,
            info={"description": "Unique identifier for the user account"},
        )
    )

    username: str
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)
    role: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="user")) 
    is_verified: bool = False
    email: str
    password_hash: str
    preferred_language: str = Field(sa_column=Column(pg.VARCHAR, server_default="en"))
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False))
    posts: List["Post"] = Relationship(back_populates="user")
    followers: list["Follow"] = Relationship(back_populates="follower", sa_relationship_kwargs= {"foreign_keys": "[Follow.follower_id]"})
    following: list["Follow"] = Relationship(back_populates="followed", sa_relationship_kwargs= {"foreign_keys": "[Follow.following_id]"})

    def __repr__(self) -> str:
        return f"<User {self.username}>"
    

class Post(SQLModel, table=True):
    __tablename__ = "posts"

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            nullable=False,
            default=uuid.uuid4,
            info={"description": "Unique identifier for the post"},
        )
    )

    caption: str
    user_id: uuid.UUID = Field(foreign_key="user_accounts.id", nullable=False)
    user: User = Relationship(back_populates="posts")
    is_reel:  bool = Field(sa_column=Column(pg.BOOLEAN, server_default="false"))
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False))
    media: List["Media"] = Relationship(back_populates="post")


class Media(SQLModel, table=True):
    __tablename__ = "media"

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            nullable=False,
            default=uuid.uuid4,
            info={"description": "Unique identifier for the media"},
        )
    )

    media_url: str
    media_order: int = Field(sa_column=Column(pg.INTEGER, nullable=False))
    media_type: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    post_id: uuid.UUID = Field(foreign_key="posts.id", nullable=False)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now)) 
    post: Optional["Post"] = Relationship(back_populates="media")

class Follow(SQLModel, table=True):
    __tablename__ = "follows"
    __table_args__ = (UniqueConstraint("follower_id", "following_id", name="uq_follower_followed"),)

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            default=uuid.uuid4,
            nullable=False,
        )
    )

    follower_id: uuid.UUID = Field(foreign_key="user_accounts.id", nullable=False)
    following_id: uuid.UUID = Field(foreign_key="user_accounts.id", nullable=False)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False))

    follower: "User" = Relationship(back_populates="following", sa_relationship_kwargs={"foreign_keys": "[Follow.follower_id]"},)
    followed: "User" = Relationship(back_populates="followers", sa_relationship_kwargs={"foreign_keys": "[Follow.following_id]"},)


class Comment(SQLModel, table=True):
    __tablename__ = "comments"

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            default=uuid.uuid4,
            nullable=False,
        )
    )

    post_id: uuid.UUID = Field(foreign_key="posts.id")
    user_id: uuid.UUID = Field(foreign_key="user_accounts.id")
    parent_comment_id: uuid.UUID | None = Field(default=None, foreign_key="comments.id")
    content: str
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False))


# class PostLike(SQLModel, table=True):
#     __tablename__ = "post_likes"

#     id: uuid.UUID = Field(
#         sa_column=Column(
#             pg.UUID,
#             primary_key=True,
#             default=uuid.uuid4,
#             nullable=False,
#         )
#     )

#     user_id: uuid.UUID = Field(foreign_key="user_accounts.id", nullable=False)
#     post_id: uuid.UUID = Field(foreign_key="posts.id", nullable=False)

#     created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))

#     __table_args__ = (
#         # prevents duplicate likes
#         {"sqlite_autoincrement": True},
#     )
