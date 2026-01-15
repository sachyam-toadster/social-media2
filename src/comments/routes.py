from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
import uuid
from src.db.base import get_session
from .schema import CommentCreate
from .models import Comment
from src.auth.dependency import get_current_user
from src.db.models import User
from sqlmodel.ext.asyncio.session import AsyncSession


comment_router = APIRouter()


@comment_router.post("/posts/{post_id}/comments")
async def create_comment(post_id: uuid.UUID,payload: CommentCreate,db: AsyncSession = Depends(get_session),current_user: User = Depends(get_current_user),
):
    parent_id = payload.parent_id

    if parent_id is not None:
        result = await db.execute(
            select(Comment.id).where(Comment.id == parent_id)
        )
        if result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent comment does not exist"
            )

    comment = Comment(
        post_id=post_id,
        user_id=current_user.id,
        content=payload.content,
        parent_comment_id=parent_id,
    )

    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment

@comment_router.get("/posts/{post_id}/comments")
async def get_comments(post_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    statement = (select(Comment).where(
    Comment.post_id == post_id,
    Comment.parent_comment_id.is_(None)
    ))

    result = await db.exec(statement)
    return result.all()

@comment_router.get("/comments/{comment_id}/replies")
async def get_replies(comment_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    statement = select(Comment).where(
        Comment.parent_comment_id == comment_id
    ).order_by(Comment.created_at.asc())

    result = await db.exec(statement)
    return result.all()

@comment_router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: uuid.UUID,db: Session = Depends(get_session),current_user: User = Depends(get_current_user),):
    result = await db.execute(
        select(Comment).where(Comment.id == comment_id)
    )
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    # delete replies first
    replies_result = await db.execute(
        select(Comment).where(Comment.parent_comment_id == comment_id)
    )
    replies = replies_result.scalars().all()

    for reply in replies:
        await db.delete(reply)

    await db.delete(comment)
    await db.commit()