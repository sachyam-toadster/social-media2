from datetime import datetime
from fastapi import Depends, HTTPException, Request, status, APIRouter
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from src.auth.dependency import get_current_user
from .schema import PostCreate, PostRead
from src.db.base import get_session
from src.db.models import Media, Post
from sqlmodel import select
import uuid

post_router = APIRouter()

@post_router.post("/create-post", status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate,db: AsyncSession = Depends(get_session),current_user: dict = Depends(get_current_user)):
    try:
        new_post = Post(
        caption=post.caption,
        is_reel=post.is_reel,
        user_id=current_user.id  
        )

        db.add(new_post)
        await db.flush()

        media_objects = [
                Media(
                    media_url=media.media_url,
                    media_order=media.media_order,
                    media_type=media.media_type,
                    post_id=new_post.id,
                )
                for media in post.media
            ]
        db.add_all(media_objects)

        await db.commit()

        return {
            "message": "Post created successfully",
            "post_id": new_post.id,
        }
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create post")


@post_router.get("/get-all-posts")
async def get_posts(db: AsyncSession = Depends(get_session)):
    statement = select(Post)
    result = await db.exec(statement)
    posts = result.all()
    return posts

@post_router.get("/get-post/{post_id}")
async def get_post(post_id: str, db: AsyncSession = Depends(get_session)):
    statement = select(Post).where(Post.id == post_id)
    result = await db.exec(statement)
    post = result.first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@post_router.delete("/delete-post/{post_id}")
async def delete_post(post_id: str, db: AsyncSession = Depends(get_session)):
    statement = select(Post).where(Post.id == post_id)
    result = await db.exec(statement)
    post = result.first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    await db.delete(post)
    await db.commit()
    return {"msg": f"Post {post_id} deleted successfully."}

@post_router.patch("/update-post/{post_id}" )
async def update_post(post_id: uuid.UUID, post_update: Post, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not Post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    post.caption = post_update.caption
    post.is_reel = post_update.is_reel
    post.updated_at = datetime.now()

    await db.commit()
    await db.refresh(post)
    return post