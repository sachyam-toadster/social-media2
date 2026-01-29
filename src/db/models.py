from datetime import datetime
import uuid
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship, PrimaryKeyConstraint
from sqlalchemy import Column, DateTime, func, UniqueConstraint, Boolean
import sqlalchemy.dialects.postgresql as pg
from .Enums import LikeTarget, MessageType


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
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False))
    media: List["Media"] = Relationship(back_populates="post",sa_relationship_kwargs={"passive_deletes": True})


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
    post_id: uuid.UUID = Field(foreign_key="posts.id", nullable=False, ondelete="CASCADE")
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

    post_id: uuid.UUID = Field(foreign_key="posts.id", ondelete="CASCADE")
    user_id: uuid.UUID = Field(foreign_key="user_accounts.id")
    parent_comment_id: uuid.UUID | None = Field(default=None, foreign_key="comments.id")
    content: str
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False))


class Like(SQLModel, table=True):
    __tablename__ = "likes"

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
            nullable=False,
        )
    )

    user_id: uuid.UUID = Field(foreign_key="user_accounts.id", nullable=False)
    target_id: uuid.UUID = Field(nullable=False )
    target_type: LikeTarget = Field(sa_column=Column(pg.ENUM(LikeTarget, name="like_target_enum"), nullable=False))

    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))

    __table_args__ = (
        # prevents duplicate likes
        {"sqlite_autoincrement": True},
    )

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            default=uuid.uuid4,
            nullable=False,
        )
    )

    is_group: bool = Field(nullable=False, default=False)
    created_by: uuid.UUID = Field(foreign_key="user_accounts.id",nullable=False,)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    last_message_at: datetime | None = Field(sa_column=Column(DateTime(timezone=True)))
    members: list["ConversationMember"] = Relationship(back_populates="conversation")
    messages: list["Message"] = Relationship(back_populates="conversation")


class ConversationMember(SQLModel, table=True):
    __tablename__ = "conversation_members"
    __table_args__ = (
        UniqueConstraint(
            "conversation_id",
            "user_id",
            name="uq_conversation_user",
        ),
    )

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            default=uuid.uuid4,
            nullable=False,
        )
    )

    conversation_id: uuid.UUID = Field(foreign_key="conversations.id",nullable=False,)
    user_id: uuid.UUID = Field(foreign_key="user_accounts.id",nullable=False,)
    joined_at: datetime = Field(sa_column=Column( DateTime(timezone=True), server_default=func.now(), nullable=False,))

    conversation: "Conversation" = Relationship(back_populates="members")
    user: "User" = Relationship()


class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            default=uuid.uuid4,
            nullable=False,
        )
    )

    conversation_id: uuid.UUID = Field(foreign_key="conversations.id",nullable=False,)
    sender_id: uuid.UUID = Field(foreign_key="user_accounts.id",nullable=False,)
    content: str | None = Field(default=None)
    media_url: str | None = Field(default=None)
    message_type: MessageType = Field(sa_column=Column(pg.ENUM(MessageType, name="message_type_enum"),nullable=False,))
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True),server_default=func.now(),nullable=False,))

    conversation: "Conversation" = Relationship(back_populates="messages")
    sender: "User" = Relationship()

class Media_User_tag(SQLModel, table=True):
    __tablename__="media_user_tag"

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            default=uuid.uuid4,
            nullable=False,
        )
    )
    
    tagged_user_id: uuid.UUID = Field(foreign_key="user_accounts.id", nullable=False,)
    tagged_by_user: uuid.UUID = Field(foreign_key = "user_accounts.id", nullable=False)
    media_id: uuid.UUID = Field(foreign_key="media.id", nullable=False)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True),server_default=func.now(),nullable=False,))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False))
    
class Story(SQLModel, table=True):
    __tablename__="stories"

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            default=uuid.uuid4,
            nullable=False,
        )
    )

    user_id: uuid.UUID = Field(foreign_key="user_accounts.id",nullable=False)
    media_url: str = Field(nullable=False)
    media_type: str = Field(nullable=False)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True),server_default=func.now(),nullable=False,))
    expires_at: datetime = Field(nullable=False)

class StoryView(SQLModel, table=True):
    __tablename__="story_views"
    
    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            default=uuid.uuid4,
            nullable=False
        )
    )

    viewer_id: uuid.UUID = Field(foreign_key="user_accounts.id",nullable=False)
    story_id: uuid.UUID = Field(foreign_key="stories.id", nullable=False)
    viewed_at: datetime = Field(sa_column=Column(DateTime(timezone=True),server_default=func.now()))
    __table_args__ = (
        UniqueConstraint("story_id", "viewer_id"),
    )

class Block(SQLModel, table=True):
    __tablename__="blocks"

    id:uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            default=uuid.uuid4,
            nullable=False
        )
    )

    blocker_id: uuid.UUID = Field(foreign_key="user_accounts.id",nullable=False)
    blocked_id: uuid.UUID = Field(foreign_key="user_accounts.id",nullable=False)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True),server_default=func.now(),nullable=False,))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False))
    
    __table_args__=(
        UniqueConstraint("blocker_id","blocked_id"),
    )