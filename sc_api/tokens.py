from fastapi import APIRouter, Body
from sc_api import core_connector # Import the core connector
from typing import Dict, Any

router = APIRouter()

@router.get("/tokens")
async def get_tokens_info(): # Renamed for clarity
    # This endpoint was not explicitly mapped to a core_connector function.
    # For now, it will return a generic message.
    # A more specific function like `get_token_details()` or `list_tokens()` could be added to core_connector.
    return {"status": "ok", "module": "tokens", "message": "Endpoint to get token information (not yet connected to specific core function)"}

@router.post("/tokens")
async def create_token_for_contribution(payload: Dict[str, str] = Body(...)):
    # Assuming the payload will contain 'contribution_id'
    # Example: {"contribution_id": "contrib123"}
    contribution_id = payload.get("contribution_id")
    if not contribution_id:
        return {"status": "error", "module": "tokens", "message": "contribution_id is required"}

    result = await core_connector.mint_token_for_contribution(contribution_id)
    return {"status": "ok", "module": "tokens", "core_response": result}
