from unittest import result
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlmodel import  func, select
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
    member_ids: list[uuid.UUID] = Body(default=[]),
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
        
    all_user_ids = member_ids + [current_user.id]

    stmt = select(User.id).where(User.id.in_(all_user_ids))
    result = await Asyncsession.execute(stmt)

    existing_ids = set(result.scalars().all())

    missing_ids = set(all_user_ids) - existing_ids

    if missing_ids:
        raise HTTPException(
            status_code=404,
            detail=f"Users not found: {list(missing_ids)}"
        )

    conversation = Conversation(is_group=is_group, created_by=current_user.id)
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
    result = await session.exec(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.first()

    if not conversation:
        raise HTTPException(404, "Conversation not found")
    if not conversation.is_group:
        raise HTTPException(
            status_code=400,
            detail="Cannot add members to private chat"
        )

    # Permission check
    if conversation.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only owner can add members"
        )

    # Add member
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
            400, "User already in conversation"
        )

    return {"message": "Member added"}


@conversation_router.delete("/{conversation_id}/members/{user_id}")
async def remove_member(
    conversation_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(ConversationMember).where(
        ConversationMember.conversation_id == conversation_id,
        ConversationMember.user_id == user_id,
    )

    conv_stmt = select(Conversation).where(Conversation.id == conversation_id)
    conv_res = await session.exec(conv_stmt)
    conversation = conv_res.first()

    if not conversation:
        raise HTTPException(404, "Conversation not found")

# Block private chats
    if not conversation.is_group:
        raise HTTPException(
            status_code=400,
            detail="Cannot remove members from private chat"
        )
     # Permission check
    if conversation.created_by != current_user.id and user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only owner can remove other members"
        )
    
    stmt = select(ConversationMember).where(
        ConversationMember.conversation_id == conversation_id,
        ConversationMember.user_id == user_id,
    )
    result = await session.exec(stmt)
    member = result.first()

    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Optional: Prevent removing last member
    member_count_stmt = select(func.count(ConversationMember.id)).where(
        ConversationMember.conversation_id == conversation_id
    )
    result = await session.exec(member_count_stmt)
    count = result.one()
    if count <= 1:
        raise HTTPException(
            400, "Cannot remove the last member of the conversation"
        )

    # Remove
    await session.delete(member)
    await session.commit()

    return {"message": "Member removed"}



