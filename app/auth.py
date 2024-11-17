

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from app.api.deps import CognitoClient
from app.models import UserSignup, UserLogin
from dataclasses import dataclass
from pydantic import EmailStr
import botocore

@dataclass
class ResponseError:
    code: str
    status_code: int
    details: str

def raise_http_exception(client_error: botocore.exceptions.ClientError, errors: list[ResponseError]) -> None:
    for error in errors:
        if client_error.response["Error"]["Code"] == error.code:
            raise HTTPException(status_code=error.status_code, detail=error.details)
    raise HTTPException(status_code=500, detail=f"{client_error}")

class Auth:
    def __init__(self, cognito: CognitoClient):
        self.cognito = cognito
    
    def signup(self, user: UserSignup):
        try:
            response = self.cognito.signup(user)
        except botocore.exceptions.ClientError as e:
            raise_http_exception(e, [
                ResponseError("UsernameExistsException", 409, "An account already exists with that specific email")
            ])
        
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            content = {
                "message": "Created user",
                "sub": response["UserSub"]
            }

            return JSONResponse(content=content, status_code=201)
        
        raise HTTPException(status_code=500, detail="Internal Server")
    
    def login(self, user: UserLogin):
        try:
            response = self.cognito.login(user)
        except botocore.exceptions.ClientError as e:
            raise_http_exception(e, [
                ResponseError("NotAuthorizedException", 401, "Username/email and password are incorrect"),
                ResponseError("UserNotFoundException", 404, "User is not found"),
                ResponseError("UserNotConfirmedException", 403, "Please verify your user account"),
            ])
        
        content = {
            "message": "User has successfully signed in",
            "AccessToken": response["AuthenticationResult"]["AccessToken"],
            "RefreshToken": response["AuthenticationResult"]["RefreshToken"]
        }

        return JSONResponse(content=content, status_code=200)

    def get_access_token(self, refresh_token: str):
        try:
            response = self.cognito.get_access_token(refresh_token)
        except botocore.exceptions.ClientError as e:
            raise_http_exception(e, [
                ResponseError("NotAuthorizedException", 401, "Refresh token is invalid"),
                ResponseError("LimitExceededException", 429, "Limit has exceeded"),
                ResponseError("InvalidParameterException", 400, "Invalid format for refresh token")
            ])

        content = {
            "message": "Successfully generated token",
            "AccessToken": response["AuthenticationResult"]["AccessToken"],
            "ExpiresIn": response["AuthenticationResult"]["ExpiresIn"],
        }

        return JSONResponse(content=content, status_code=200)
    
    def get_user_info(self, access_token: str):
        try:
            response = self.cognito.user_exists(access_token)
        except botocore.exceptions.ClientError as e:
            raise_http_exception([
                ResponseError("UserNotFoundException", 404, "User cannot be found")
            ])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{e}")
        
        content = {attribute["Name"]: attribute["Value"] for attribute in response["UserAttributes"]}

        return JSONResponse(content=content, status_code=200)

    def logout(self, access_token: str):
        try:
            self.cognito.logout(access_token)
        except botocore.exceptions.ClientError as e:
            raise_http_exception(e, [
                ResponseError("NotAuthorizedException", 401, "Access token is invalid"),
                ResponseError("TooManyRequestsException", 429, "Too many requests"),
                ResponseError("InvalidParameterException", 400, "Wrong format of access token"),
            ])
        
        return JSONResponse(content={"message": "success"}, status_code=200)

