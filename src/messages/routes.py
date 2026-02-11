from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
import uuid
from datetime import datetime

from src.block.service import _check_block_between_users
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
    
    if not content and not media_url:
        raise HTTPException(
            status_code=400,
            detail="Message must contain text or media"
        )

    # 2️⃣ Conversation exists
    conversation = await session.get(Conversation, conversation_id)

    if not conversation:
        raise HTTPException(404, "Conversation not found")
    
    # check membership  
    stmt = select(ConversationMember).where(
        ConversationMember.conversation_id == conversation_id,
        ConversationMember.user_id == current_user.id,
    )

    result = await session.exec(stmt)
    member = result.first()

    if not member:
        raise HTTPException(status_code=403, detail="Not a conversation member")
    
    if not conversation.is_group:

        stmt = select(ConversationMember.user_id).where(
            ConversationMember.conversation_id == conversation_id,
            ConversationMember.user_id != current_user.id,
        )

        result = await session.exec(stmt)
        other_user_id = result.one()

        blocked = await _check_block_between_users(
            current_user.id,
            other_user_id,
            session,
        )

        if blocked:
            raise HTTPException(
                status_code=403,
                detail="You cannot message this user"
            )

    if content and media_url:
        msg_type = "mixed"
    elif content:
        msg_type = "text"
    else:
        msg_type = "media"

    message = Message(
        conversation_id=conversation_id,
        sender_id=current_user.id,
        content=content,
        media_url=media_url,
        message_type=msg_type,
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

