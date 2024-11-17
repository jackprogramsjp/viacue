from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "viacue"
    API_V1_STR: str = "/api/v1"

    # This is for the 511 Bay Area Transit API system
    # https://511.org/sites/default/files/pdfs/511%20SF%20Bay%20Open%20Data%20Specification%20-%20Transit.pdf
    TRANSIT_API_KEY: str

    # Amazon Web Service
    AWS_REGION_NAME: str = "us-west-2"

    # Amazon Cognito
    AWS_COGNITO_CLIENT_ID: str
    AWS_COGNITO_USER_POOL_ID: str

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
