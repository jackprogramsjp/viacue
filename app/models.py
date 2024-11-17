from annotated_types import MinLen
from typing import Annotated
from pydantic import BaseModel, EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    password: Annotated[str, MinLen(8)]

class UserSignup(BaseModel):
    email: EmailStr
    password: Annotated[str, MinLen(8)]
    language: Annotated[str, MinLen(1)]
    accommodation: Annotated[str, MinLen(1)]

class RefreshToken(BaseModel):
    refresh_token: str

class AccessToken(BaseModel):
    access_token: str
