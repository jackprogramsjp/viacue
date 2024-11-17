import uuid

from annotated_types import MinLen, MaxLen
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

class UserVerification(BaseModel):
    email: EmailStr
    confirmation: Annotated[str, MaxLen(6)]
