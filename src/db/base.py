from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.config import settings

DATABASE_URL = settings.database_url

engine = create_engine(
    DATABASE_URL,

)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    db = SessionLocal()
    try:
        print("DATABASE URL:", settings.database_url)
        yield db
    finally:
        db.close()


def initdb():
    return engine
