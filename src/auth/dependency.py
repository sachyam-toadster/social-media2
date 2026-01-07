from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from src.auth.service import UserService
from src.db.base import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any
from src.db.models import User


class TokenBearer(HTTPBearer):

    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

class AccessTokenBearer(TokenBearer):

    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide an access token",
            )
        
        
def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_db),
):
    user_email = token_details["user"]["email"]

    user_service = UserService()
    user = user_service.get_user_by_email(user_email, session)

    return user

class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
        if current_user.role in self.allowed_roles:
            return True

        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to perform this action."
        )