from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager
import asyncio
import logging
from src.auth.routes import auth_router
from src.posts.routes import post_router
from src.follows.routes import follow_router
from src.comments.routes import comment_router
from src.likes.routes import like_router
from src.conversations.routes import conversation_router
from src.messages.routes import message_router
from src.tag.routes import tag_router
from src.stories.routes import stories_router
from src.block.routes import block_router
from src.db.base import engine

logger = logging.getLogger(__name__)


async def check_database_connection(max_retries=10, retry_delay=2):
    """Check if database is ready to accept connections"""
    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(lambda x: None)
            logger.info("✓ Database connection successful")
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(
                    f"Database connection failed (attempt {attempt + 1}/{max_retries}). "
                    f"Retrying in {retry_delay}s... Error: {str(e)}"
                )
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"Failed to connect to database after {max_retries} attempts")
                raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Application starting up...")
    await check_database_connection()
    logger.info("Application startup complete")
    yield
    # Shutdown
    logger.info("Application shutting down...")
    await engine.dispose()
    logger.info("Application shutdown complete")


app = FastAPI(lifespan=lifespan)

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

app.include_router(
    like_router,
    tags=["like"]
)

app.include_router(
    conversation_router,
    tags=["convo"]
)

app.include_router(
    message_router,
    tags=["Messages"]
)

app.include_router(
    tag_router,
    tags=["tag"]
)

app.include_router(
    stories_router,
    tags=["story"]
)

app.include_router(
    block_router,
    tags=["block"]
)
