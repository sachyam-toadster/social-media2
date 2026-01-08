from pydantic import BaseModel, Field, EmailStr
from typing import List


class UserCreateModel(BaseModel):
    first_name: str = Field(max_length=25)
    last_name:  str = Field(max_length=25)
    username: str = Field(max_length=8)
    email: EmailStr
    password: str  = Field(min_length=6)

class UserLoginModel(BaseModel):
    email: EmailStr
    password: str

class UserProfileModel(BaseModel):
    first_name: str | None
    last_name: str | None
    username: str
    email:  EmailStr

class EmailModel(BaseModel):
    addresses : List[str]

class PasswordResetRequestModel(BaseModel):
    email: str

class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str
