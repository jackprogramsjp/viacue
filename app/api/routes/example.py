import uuid
from typing import Any

from fastapi import APIRouter

router = APIRouter()

@router.get("/example")
def read_example():
    return {"message": "hello world"}
