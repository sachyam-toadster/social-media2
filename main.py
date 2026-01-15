from fastapi import FastAPI,APIRouter
from src.auth.routes import auth_router
from src.posts.routes import post_router
from src.follows.routes import follow_router
from src.comments.routes import comment_router

app = FastAPI()

@app.get('/')
async def read_root():
    return {"message": "Hello World!"}

app.include_router(
    auth_router,
    prefix="/api",
    tags=["auth"]
    )

app.include_router(
    post_router,
    prefix="/api/posts",
    tags=["posts"]
    )

app.include_router(
    follow_router,
    tags=["follow"]

)
app.include_router(
    comment_router,
    tags=["comments"]
)