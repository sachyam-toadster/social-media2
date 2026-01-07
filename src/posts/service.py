from sqlmodel import Session
from app.posts.model import Post
from uuid import UUID

def create_post(
    user_id: UUID,
    data,
    session: Session
) -> Post:
    post = Post(
        user_id=user_id,
        caption=data.caption,
        media_url=data.media_url,
        is_reel=data.is_reel
    )
    session.add(post)
    session.commit()
    session.refresh(post)
    return post
