from datetime import datetime
from fastapi import Depends, HTTPException, Request, status, APIRouter
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.exc import SQLAlchemyError
from src.auth.dependency import get_current_user
from src.db.base import get_session
from src.db.models import Follow, User
import uuid



follow_router = APIRouter()

@follow_router.post("/users/{user_id}/follow", status_code=201)
async def follow_user(user_id: uuid.UUID, current_user: dict = Depends(get_current_user), session: AsyncSession = Depends(get_session),):
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
async def unfollow_user(user_id: uuid.UUID, current_user: dict = Depends(get_current_user), session: AsyncSession = Depends(get_session),):
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


@follow_router.get("/users/{user_id}/followers")
async def get_followers(user_id: uuid.UUID, session: AsyncSession = Depends(get_session),):
    stmt = (
        select(User)
        .join(Follow, Follow.follower_id == User.id)
        .where(Follow.following_id == user_id)
    )
    result = await session.scalars(stmt)
    return result.all()

