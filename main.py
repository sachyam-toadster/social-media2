from fastapi import FastAPI,APIRouter
from src.auth.routes import auth_router
from src.posts.routes import post_router

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