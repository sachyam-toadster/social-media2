from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlmodel import select
from uuid import UUID
import uuid
from src.db.base import get_session
from src.auth.dependency import get_current_user
from src.db.models import User, Media_User_tag, Media, Post
from .schema import TagUserCreate
from sqlmodel.ext.asyncio.session import AsyncSession

tag_router = APIRouter()

@tag_router.post("/media/{media_id}/tag-user", status_code=status.HTTP_201_CREATED)
async def tag_user_on_media(
    media_id: UUID,
    payload: TagUserCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # 1️⃣ Fetch media
    result = await db.execute(select(Media).where(Media.id == media_id))
    media = result.scalar_one_or_none()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    # 2️⃣ Check ownership via post
    result = await db.execute(select(Post).where(Post.id == media.post_id))
    post = result.scalar_one_or_none()
    if not post or post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to tag users")

    # 3️⃣ Prevent duplicate tag
    result = await db.execute(
        select(Media_User_tag).where(
            Media_User_tag.media_id == media_id,
            Media_User_tag.tagged_user_id == payload.tagged_user_id
        )
    )
    existing_tag = result.scalar_one_or_none()
    if existing_tag:
        raise HTTPException(status_code=400, detail="User already tagged")

    # 4️⃣ Create tag
    tag = Media_User_tag(
        media_id=media_id,
        tagged_user_id=payload.tagged_user_id,
        tagged_by_user=current_user.id
    )
    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    return tag

@tag_router.delete("/media/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_tagged_user(
    tag_id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # 1️⃣ Get tag
    tag = await db.get(Media_User_tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # 2️⃣ Get media
    result = await db.execute(select(Media).where(Media.id == tag.media_id))
    media = result.scalar_one_or_none()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    # 3️⃣ Get post for ownership check
    result = await db.execute(select(Post).where(Post.id == media.post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # 4️⃣ Permission check
    if current_user.id not in {post.user_id, tag.tagged_user_id}:
        raise HTTPException(status_code=403, detail="Not allowed to remove this tag")

    # 5️⃣ Delete tag
    await db.delete(tag)
    await db.commit()

