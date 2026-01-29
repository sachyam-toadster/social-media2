from datetime import datetime
from typing import List
from fastapi import Depends, HTTPException, Request, status, APIRouter
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import or_, select, and_
from sqlalchemy.exc import SQLAlchemyError
from src.auth.dependency import get_current_user
from src.block.service import interaction_guard
from src.db.base import get_session
from src.db.models import Follow, User, Block
from .schema import FollowUserResponse, FollowerResponse
import uuid



follow_router = APIRouter()

@follow_router.post("/users/{user_id}/follow",status_code=201,)
async def follow_user(user_id: uuid.UUID, _: bool = Depends(interaction_guard), current_user: dict = Depends(get_current_user), session: AsyncSession = Depends(get_session),):
    if user_id == current_user.id:
        raise HTTPException(400, "You cannot follow yourself")

    stmt = select(Follow).where(
        Follow.follower_id == current_user.id,
        Follow.following_id == user_id,
    )
    existing = await session.scalar(stmt)

    if existing:
        raise HTTPException(409, "Already following this user")

    follow = Follow(
        follower_id=current_user.id,
        following_id=user_id,
    )

    session.add(follow)
    await session.commit()

    return {"message": "User followed successfully"}


@follow_router.delete("/users/{user_id}/unfollow", status_code=200)
async def unfollow_user(user_id: uuid.UUID,  _: bool = Depends(interaction_guard), current_user: dict = Depends(get_current_user), session: AsyncSession = Depends(get_session),):
    stmt = select(Follow).where(
        Follow.follower_id == current_user.id,
        Follow.following_id == user_id,
    )
    follow = await session.scalar(stmt)

    if not follow:
        raise HTTPException(404, "You are not following this user")

    await session.delete(follow)
    await session.commit()

    return {"message": "User unfollowed successfully"}


@follow_router.get("/users/{user_id}/followers", response_model=List[FollowerResponse])
async def get_followers(user_id: uuid.UUID, current_user: dict = Depends(get_current_user), session: AsyncSession = Depends(get_session),):
    result = await session.execute(
        select(Block).where(
            or_(
                and_(
                    Block.blocker_id == current_user.id,
                    Block.blocked_id == user_id
                ),
                and_(
                    Block.blocker_id == user_id,
                    Block.blocked_id == current_user.id
                )
            )
        )
    )

    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=403,
            detail="Block h bhai"
        )
    
    stmt = (
        select(User)
        .join(Follow, Follow.follower_id == User.id)
        .where(Follow.following_id == user_id)
    )
    result = await session.scalars(stmt)
    return result.all()

