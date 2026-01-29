from datetime import datetime, timedelta
from typing import List
from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.dependency import get_current_user
from .schema import StoryCreate, StoryRead
from src.db.base import get_session
from src.db.models import Story, StoryView, User, Follow
from sqlmodel import select
from .schema import StoryRead,StoryCreate, StoryViewerOut
import uuid


stories_router = APIRouter()

@stories_router.post("/stories", response_model=StoryRead)
async def create_story(
    data: StoryCreate,
    db: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user)
):

    expires_at = datetime.utcnow() + timedelta(hours=24)

    story = Story(
        user_id=current_user.id,
        media_url=data.media_url,
        media_type=data.media_type,
        expires_at=expires_at
    )

    db.add(story)
    await db.commit()
    await db.refresh(story)

    return story

@stories_router.get("/stories", response_model=List[StoryRead])
async def get_stories(
    db: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user)
):

    now = datetime.utcnow()

    following_subquery = (
        select(Follow.following_id)
        .where(Follow.follower_id == current_user.id)
    )

    result = await db.exec(
        select(Story)
        .where(
            Story.expires_at > now,
            (
                (Story.user_id == current_user.id) |
                (Story.user_id.in_(following_subquery))
            )
        )
        .order_by(Story.created_at.desc())
    )

    stories = result.all()

    return stories

@stories_router.post("/stories/{story_id}/view")
async def view_story(
    story_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user)
):

    result = await db.exec(select(Story).where(Story.id == story_id))
    story = result.first()  # now this works

    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    if story.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Story has expired")
    
    if story.user_id != current_user.id:

        result = await db.exec(
            select(Follow).where(
                Follow.follower_id == current_user.id,
                Follow.following_id == story.user_id
            )
        )

        follow = result.first()

        if not follow:
            raise HTTPException(
                status_code=403,
                detail="You are not allowed to view this story"
            )

    result = await db.exec(
        select(StoryView).where(
            StoryView.story_id == story_id,
            StoryView.viewer_id == current_user.id
        )
    )
    existing_view = result.first()

    if existing_view:
        return {"message": "Story already viewed"}
    
    new_view = StoryView(
        story_id=story_id,
        viewer_id=current_user.id
    )

    db.add(new_view)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        return {"message": "Story already viewed"}

    return {"message": "Story viewed successfully"}
    

@stories_router.delete("/stories/{story_id}")
async def delete_story(
    story_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user)
):

    story = await db.get(Story, story_id)

    if not story:
        raise HTTPException(404)

    if story.user_id != current_user.id:
        raise HTTPException(403)

    await db.delete(story)
    await db.commit()

    return {"message": "Deleted"}

@stories_router.get("/stories/{story_id}/views", response_model=list[StoryViewerOut])
async def get_story_views(
    story_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    # 1️⃣ Check story exists
    story = await db.get(Story, story_id)

    if not story:
        raise HTTPException(
            status_code=404,
            detail="Story not found"
        )

    # 2️⃣ Only owner can see viewers
    if story.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not allowed to view story viewers"
        )

    # 3️⃣ Get viewers
    stmt = (
        select(
            StoryView.viewer_id,
            User.username,
            StoryView.viewed_at
        )
        .join(User, User.id == StoryView.viewer_id)
        .where(StoryView.story_id == story_id)
        .order_by(StoryView.viewed_at.desc())
    )

    result = await db.exec(stmt)
    results = result.all()

    # 4️⃣ Format response
    return [
        StoryViewerOut(
            user_id=row.viewer_id,
            username=row.username,
        )
        for row in results
    ]
