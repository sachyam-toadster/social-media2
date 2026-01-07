import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
from .schemas import UserCreateModel, UserLoginModel, UserProfileModel
from src.db.models import User
from src.auth.utils import generate_password_hash, verify_password

class UserService:
    
    def get_user_by_email(self, email: str, session: Session):
        statement = select(User).where(User.email == email)
        result = session.execute(statement)
        return result.scalar_one_or_none()

    def user_exists(self, email: str, session: Session) -> bool:
        return self.get_user_by_email(session, email) is not None

    @staticmethod
    def create_user(session: Session, user_data: UserCreateModel):
        data = user_data.model_dump()

        new_user = User(
            email=data["email"],
            username=data["username"],
            password_hash=generate_password_hash(data["password"]),
            is_verified=False
        )

        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user
