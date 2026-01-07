from pydantic import BaseModel, Field, EmailStr



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
    first_name: str
    last_name: str
    username: str
    email:  EmailStr