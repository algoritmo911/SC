from fastapi import APIRouter, Path, Body # Added Path for path parameters
from sc_api import core_connector # Import the core connector
from typing import Dict, Any

router = APIRouter()

# Changed to /users/{user_id} to align with get_user_by_id core_connector function
@router.get("/users/{user_id}")
async def get_user(user_id: str = Path(..., title="The ID of the user to get")):
    result = await core_connector.get_user_by_id(user_id)
    return {"status": "ok", "module": "users", "core_response": result}

@router.post("/users")
async def create_user(user_data: Dict[Any, Any] = Body(...)):
    # This endpoint was not explicitly mapped to a core_connector function.
    # For now, it will return a generic message.
    # A more specific function like `create_new_user(user_data)` could be added to core_connector.
    print(f"API: Received request to create user with data: {user_data}")
    return {"status": "ok", "module": "users", "message": "Endpoint to create a user (not yet connected to core)", "received_data": user_data}
