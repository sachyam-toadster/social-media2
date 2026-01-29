from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, delete, select
import uuid
from src.db.base import get_session
from src.auth.dependency import get_current_user
from src.db.models import Block, Follow
from sqlmodel.ext.asyncio.session import AsyncSession


block_router = APIRouter()

@block_router.post("/users/{user_id}/block")
async def block_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user)
):

    if user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot block yourself"
        )

    # Check if already blocked
    result = await db.exec(
        select(Block).where(
            Block.blocker_id == current_user.id,
            Block.blocked_id == user_id
        )
    )

    if result.first():
        return {"message": "User already blocked"}
    
    await db.exec(
        delete(Follow).where(
            Follow.follower_id == current_user.id,
            Follow.following_id == user_id
        )
    )

    # 3️⃣ Remove follow (user -> current)
    await db.exec(
        delete(Follow).where(
            Follow.follower_id == user_id,
            Follow.following_id == current_user.id
        )
    )

    block = Block(
        blocker_id=current_user.id,
        blocked_id=user_id
    )

    db.add(block)

    await db.commit()

    return {"message": "User blocked successfully"}

@block_router.delete("/users/{user_id}/unblock")
async def unblock_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user)
):

    result = await db.exec(
        select(Block).where(
            Block.blocker_id == current_user.id,
            Block.blocked_id == user_id
        )
    )

    block = result.first()

    if not block:
        raise HTTPException(404, "User not blocked")

    await db.delete(block)
    await db.commit()

    return {"message": "User unblocked"}

