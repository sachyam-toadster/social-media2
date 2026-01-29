from fastapi import HTTPException, status
from fastapi.params import Depends
from sqlalchemy import exists, or_, and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.dependency import get_current_user
from src.db.Enums import LikeTarget
from src.db.base import get_session
from src.db.models import Block, User, Post
import uuid


async def _check_block_between_users(
    user_a: uuid.UUID,
    user_b: uuid.UUID,
    db: AsyncSession,
):
    stmt = select(Block.id).where(
        or_(
            and_(
                Block.blocker_id == user_a,
                Block.blocked_id == user_b,
            ),
            and_(
                Block.blocker_id == user_b,
                Block.blocked_id == user_a,
            ),
        )
    )

    result = await db.execute(stmt)

    return result.first() is not None

async def interaction_guard(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    blocked = await _check_block_between_users(
        current_user.id,
        user_id,
        db,
    )

    if blocked:
        raise HTTPException(
            status_code=403,
            detail="You cannot interact with this user",
        )

    return True

async def feed_block_filter(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Block).where(
        or_(
            Block.blocker_id == current_user.id,
            Block.blocked_id == current_user.id,
        )
    )

    result = await db.execute(stmt)

    blocked_ids = set()

    for block in result.scalars():
        if block.blocker_id == current_user.id:
            blocked_ids.add(block.blocked_id)
        else:
            blocked_ids.add(block.blocker_id)

    return blocked_ids

async def comment_guard(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    post = await db.get(Post, post_id)

    if not post:
        raise HTTPException(404, "Post not found")

    blocked = await _check_block_between_users(
        current_user.id,
        post.user_id,
        db,
    )

    if blocked:
        raise HTTPException(403, "Blocked")

    return post

from src.db.models import Post, Comment


async def like_guard(
    target_type: LikeTarget,
    target_id: uuid.UUID,

    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Get target
    if target_type == LikeTarget.POST:
        target = await db.get(Post, target_id)

        if not target:
            raise HTTPException(404, "Post not found")

        owner_id = target.user_id

    elif target_type == LikeTarget.COMMENT:
        target = await db.get(Comment, target_id)

        if not target:
            raise HTTPException(404, "Comment not found")

        owner_id = target.user_id

    else:
        raise HTTPException(400, "Invalid target type")

    # Block check
    blocked = await _check_block_between_users(
        current_user.id,
        owner_id,
        db,
    )

    if blocked:
        raise HTTPException(403, "Blocked")

    return target   # 👈 optional, if needed later
