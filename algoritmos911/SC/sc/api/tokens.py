# sc/api/tokens.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_tokens():
    return {"message": "GET tokens endpoint"}

@router.post("/")
async def post_tokens():
    return {"message": "POST tokens endpoint"}
