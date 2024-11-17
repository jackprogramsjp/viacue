import boto3
from app.core.config import settings
from app.models import UserSignup, UserLogin


class CognitoClient:
    def __init__(self):
        self.client = boto3.client("cognito-idp", region_name=settings.AWS_REGION_NAME)
    
    def signup(self, user: UserSignup):
        return self.client.sign_up(
            ClientId=settings.AWS_COGNITO_CLIENT_ID,
            Username=user.email,
            Password=user.password,
            UserAttributes=[
                {
                    "Name": "custom:language",
                    "Value": user.language,
                },
                {
                    "Name": "custom:accommodation",
                    "Value": user.accommodation,
                },
            ],
        )
    
    def login(self, user: UserLogin):
        return self.client.initiate_auth(
            AuthParameters={
                "USERNAME": user.email,
                "PASSWORD": user.password,
            },
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=settings.AWS_COGNITO_CLIENT_ID,
        )

def get_cognito_client() -> CognitoClient:
    return CognitoClient()
