from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
import uuid
from src.block.service import like_guard
from src.db.Enums import LikeTarget
from src.db.base import get_session
from  src.db.models import User,Like, Comment, Post
from src.auth.dependency import get_current_user
from sqlmodel.ext.asyncio.session import AsyncSession


like_router = APIRouter()


@like_router.post("/likes/{target_type}/{target_id}")
async def like_unlike(target_type: LikeTarget,target_id: uuid.UUID, _: object = Depends(like_guard),db: AsyncSession = Depends(get_session),current_user: User = Depends(get_current_user),  ):  
    if target_type == LikeTarget.POST:
        target = await db.get(Post, target_id)
        if not target:
            raise HTTPException(status_code=404, detail="Post not found")
    elif target_type == LikeTarget.COMMENT:
        target = await db.get(Comment, target_id)
        if not target:
            raise HTTPException(status_code=404, detail="Comment not found")
    else:
        raise HTTPException(status_code=400, detail="Invalid target type")

    statement = select(Like).where(
        Like.user_id == current_user.id,
        Like.target_id == target_id,
        Like.target_type == target_type
    )
    
    # await the execution
    result = await db.exec(statement)
    existing_like = result.first()

    if existing_like:
        # UNLIKE
        await db.delete(existing_like)
        await db.commit()
        return {"liked": False}

    # LIKE
    like = Like(
        user_id=current_user.id,
        target_id=target_id,
        target_type=target_type
    )

    db.add(like)
    await db.commit()

    return {"liked": True}

@like_router.get("/likes/{target_type}/{target_id}/count")
async def get_likes_count(
    target_type: LikeTarget,
    target_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
):
    if target_type == LikeTarget.POST:
        target = await db.get(Post, target_id)
        if not target:
            raise HTTPException(status_code=404, detail="Post not found")
    elif target_type == LikeTarget.COMMENT:
        target = await db.get(Comment, target_id)
        if not target:
            raise HTTPException(status_code=404, detail="Comment not found")
    else:
        raise HTTPException(status_code=400, detail="Invalid target type")

    statement = select(Like).where(
        Like.target_id == target_id,
        Like.target_type == target_type
    )
    result = await db.exec(statement)
    likes = result.all()
    return {"likes_count": len(likes)}


@like_router.get("/likes/{target_type}/{target_id}/is-liked")
async def is_liked(target_type: LikeTarget,target_id: uuid.UUID,_: object = Depends(like_guard),db: AsyncSession = Depends(get_session),current_user: User = Depends(get_current_user),):
    if target_type == LikeTarget.POST:
        target = await db.get(Post, target_id)
        if not target:
            raise HTTPException(status_code=404, detail="Post not found")
    elif target_type == LikeTarget.COMMENT:
        target = await db.get(Comment, target_id)
        if not target:
            raise HTTPException(status_code=404, detail="Comment not found")
    else:
        raise HTTPException(status_code=400, detail="Invalid target type")
    
    statement = select(Like).where(
        Like.user_id == current_user.id,
        Like.target_id == target_id,
        Like.target_type == target_type
    )
    result = await db.exec(statement)
    like = result.first()
    return {"liked": bool(like)}
