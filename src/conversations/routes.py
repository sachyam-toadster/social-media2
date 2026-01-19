from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import  select
from datetime import datetime
import uuid

from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.base import get_session
from src.db.models import Conversation, ConversationMember, Message
from src.auth.dependency import get_current_user
from src.db.models import User

conversation_router = APIRouter(prefix="/conversations", tags=["Conversations"])

@conversation_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_conversation(
    is_group: bool = False,
    member_ids: list[uuid.UUID] = [],
    Asyncsession: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    conversation = Conversation(is_group=is_group)
    Asyncsession.add(conversation)
    await Asyncsession.commit()
    await Asyncsession.refresh(conversation)

    # add creator
    Asyncsession.add(
        ConversationMember(
            conversation_id=conversation.id,
            user_id=current_user.id,
        )
    )

    # add other members
    for user_id in member_ids:
        Asyncsession.add(
            ConversationMember(
                conversation_id=conversation.id,
                user_id=user_id,
            )
        )

    await Asyncsession.commit()
    return conversation


@conversation_router.get("/")
async def get_my_conversations(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Conversation)
        .join(ConversationMember)
        .where(ConversationMember.user_id == current_user.id)
        .order_by(Conversation.last_message_at.desc())
    )
    result = await session.exec(stmt)
    return result.all()


@conversation_router.post("/{conversation_id}/members")
async def add_member(
    conversation_id: uuid.UUID,
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    member = ConversationMember(
        conversation_id=conversation_id,
        user_id=user_id,
    )

    session.add(member)
    try:
        session.commit()
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail="User already in conversation",
        )

    return {"message": "Member added"}


@conversation_router.delete("/{conversation_id}/members/{user_id}")
async def remove_member(
    conversation_id: uuid.UUID,
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(ConversationMember).where(
        ConversationMember.conversation_id == conversation_id,
        ConversationMember.user_id == user_id,
    )

    result = await session.exec(stmt)
    member = result.first()

    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    await session.delete(member)
    await session.commit()
    return {"message": "Member removed"}


