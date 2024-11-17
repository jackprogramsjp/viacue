from fastapi import APIRouter

from app.api.routes import example, login, transit

api_router = APIRouter()
api_router.include_router(example.router, tags=["example"])
api_router.include_router(login.router, tags=["login"])
api_router.include_router(transit.router, tags=["transit"])