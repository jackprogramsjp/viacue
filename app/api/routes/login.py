import hmac
import hashlib
import base64
import boto3
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.core.config import settings
from app.api.deps import get_cognito_client, CognitoClient
from app.models import UserSignup, UserLogin, UserVerification
from app.auth import Auth

router = APIRouter()

@router.post('/auth/signup', tags=['Auth'])
async def login(user: UserSignup, cognito: CognitoClient = Depends(get_cognito_client)):
    return Auth(cognito).signup(user)

@router.post('/auth/login', tags=['Auth'])
async def login(user: UserLogin, cognito: CognitoClient = Depends(get_cognito_client)):
    return Auth(cognito).login(user)
