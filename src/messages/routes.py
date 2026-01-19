from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
import uuid
from datetime import datetime

from src.db.base import get_session
from src.db.models import Message, ConversationMember, Conversation
from src.auth.dependency import get_current_user
from src.db.models import User

message_router = APIRouter(prefix="/messages", tags=["Messages"])


@message_router.post("/", status_code=201)
async def send_message(
    conversation_id: uuid.UUID,
    content: str | None = None,
    media_url: str | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # check membership  
    stmt = select(ConversationMember).where(
        ConversationMember.conversation_id == conversation_id,
        ConversationMember.user_id == current_user.id,
    )

    result = await session.exec(stmt)
    member = result.first()

    if not member:
        raise HTTPException(status_code=403, detail="Not a conversation member")

    message = Message(
        conversation_id=conversation_id,
        sender_id=current_user.id,
        content=content,
        media_url=media_url,
        message_type="text" if content else "media",
    )

    session.add(message)

    # update last_message_at
    conversation = await session.get(Conversation, conversation_id)
    conversation.last_message_at = datetime.utcnow()

    await session.commit()
    await session.refresh(message)
    return message

@message_router.get("/{conversation_id}")
async def get_messages(
    conversation_id: uuid.UUID,
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    stmt = select(ConversationMember).where(
        ConversationMember.conversation_id == conversation_id,
        ConversationMember.user_id == current_user.id,
    )

    result = await session.exec(stmt)
    member = result.first()

    if not member:
        raise HTTPException(status_code=403, detail="Not a conversation member")

    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await session.exec(stmt)
    messages = result.all()

    return messages

