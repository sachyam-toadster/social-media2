from fastapi import APIRouter, status, Depends
from src.auth.dependency import get_current_user, RoleChecker
from src.auth.schemas import UserCreateModel, UserLoginModel, UserProfileModel
from src.auth.utils import verify_password
from src.db.base import get_db
from sqlalchemy.orm import Session
from .service import UserService
from .utils import create_access_token
from datetime import datetime, timedelta
from src.config import settings
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

auth_router = APIRouter()
user_service = UserService()



@auth_router.post('/signup', status_code=status.HTTP_201_CREATED)
async def create_user_account(user_data: UserCreateModel, session: Session = Depends(get_db)):
    email = user_data.email

    user_exist = user_service.user_exists(email, session)

    if user_exist:
        return {"error": "User with this email already exists."}
    new_user = user_service.create_user(session, user_data)
    
    return {"message": "User created successfully", "user_uid": str(new_user.uid)}


@auth_router.post("/login")
def login_users(
    login_data: UserLoginModel, session: Session = Depends(get_db)
):
    email = login_data.email
    password = login_data.password

    user = user_service.get_user_by_email(email, session)


    if user is not None:
        password_valid = verify_password(password, user.password_hash)

        if password_valid:
            access_token = create_access_token(
                user_data={"email": user.email, "user_uid": str(user.id)}
            )

            refresh_token = create_access_token(
                user_data={"email": user.email, "user_uid": str(user.id)},
                refresh=True,
                expiry=timedelta(days=settings.REFRESH_TOKEN_EXPIRY),
            )

            return JSONResponse(
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {"email": user.email, "uid": str(user.id)},
                }
            )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Email Or Password"
    )


@auth_router.get('/logout')
async def logout():

    return {"message": "User logout endpoint"}

@auth_router.get('/refresh-token')
async def get_new_access_token():
    return {"message": "User refresh token endpoint"}

@auth_router.get('/me', response_model=UserProfileModel)
async def get_current_user_profile(
    user=Depends(get_current_user), _: bool = Depends(RoleChecker(allowed_roles=["admin", "user",]))
):
    return user
    


@auth_router.post('/password-reset-request')
async def password_reset_request():
    return {"message": "Password reset request endpoint"}

@auth_router.post('/password-reset-confirm')
async def password_reset():
    return {"message": "Password reset endpoint"}

@auth_router.post('/verify-email')
async def verify_email():
    return {"message": "Email verification endpoint"}

@auth_router.get("/refresh-token")
async def get_refresh_token():
    return {"message": "User refresh token endpoint"}
