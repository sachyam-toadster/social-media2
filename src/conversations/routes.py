from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import  select
import uuid

from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.base import get_session
from src.db.models import Conversation, ConversationMember
from src.auth.dependency import get_current_user
from src.db.models import User

conversation_router = APIRouter(prefix="/conversations", tags=["convo"])

@conversation_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_conversation(
    is_group: bool = False,
    member_ids: list[uuid.UUID] | None=None,
    Asyncsession: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    member_ids = member_ids or []
    member_ids = list(set(member_ids) - {current_user.id})

    if not is_group:
        if len(member_ids) != 1:
            raise HTTPException(
                status_code=400,
                detail="one-to-one chat must have exactly one other user"
            )
    else:
        if len(member_ids) < 2:
            raise HTTPException(
                status_code=400,
                detail="Group chat must have at least 2 members"
            )
        
    conversation = Conversation(is_group=is_group)
    Asyncsession.add(conversation)
    await Asyncsession.flush()

    all_user_ids = member_ids + [current_user.id]
    members = [
        ConversationMember(
            conversation_id=conversation.id,
            user_id=user_id
        )
        for user_id in all_user_ids
    ]

    Asyncsession.add_all(members)
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
        await session.commit()
    except Exception:
        await session.rollback()
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


