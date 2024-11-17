from fastapi import APIRouter, Depends, status
from app.api.deps import get_cognito_client, CognitoClient
from app.models import UserSignup, UserLogin, RefreshToken, AccessToken
from app.auth import Auth
from pydantic import EmailStr

router = APIRouter()

@router.post('/auth/signup', status_code=status.HTTP_201_CREATED, tags=['Auth'])
async def login(user: UserSignup, cognito: CognitoClient = Depends(get_cognito_client)):
    return Auth(cognito).signup(user)

@router.post('/auth/login', status_code=status.HTTP_200_OK, tags=['Auth'])
async def login(user: UserLogin, cognito: CognitoClient = Depends(get_cognito_client)):
    return Auth(cognito).login(user)

@router.post('/auth/logout', status_code=status.HTTP_200_OK, tags=['Auth'])
async def logout(access_token: AccessToken, cognito: CognitoClient = Depends(get_cognito_client)):
    return Auth(cognito).logout(access_token.access_token)

@router.post('/auth/userinfo', status_code=status.HTTP_200_OK, tags=['Auth'])
async def get_user_info(access_token: AccessToken, cognito: CognitoClient = Depends(get_cognito_client)):
    return Auth(cognito).get_user_info(access_token.access_token)

@router.post('/auth/access_token', status_code=status.HTTP_200_OK, tags=["Auth"])
async def get_access_token(refresh_token: RefreshToken, cognito: CognitoClient = Depends(get_cognito_client)):
    return Auth(cognito).get_access_token(refresh_token.refresh_token)
