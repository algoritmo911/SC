# sc/api/users.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_users():
    return {"message": "GET users endpoint"}

@router.post("/")
async def post_users():
    return {"message": "POST users endpoint"}
