from fastapi import APIRouter, Body
from sc_api import core_connector # Import the core connector
from typing import Dict, Any


router = APIRouter()

@router.get("/knowledge")
async def get_knowledge_entries(): # Renamed for clarity, though not strictly required by task
    # This endpoint was not explicitly mapped to a core_connector function.
    # For now, it will return a generic message.
    # A more specific function like `get_knowledge_entries_list()` could be added to core_connector.
    return {"status": "ok", "module": "knowledge", "message": "Endpoint to list knowledge entries (not yet connected to core)"}

@router.post("/knowledge")
async def create_knowledge_entry(entry: Dict[Any, Any] = Body(...)):
    # Connect to the core_connector's submit_knowledge_entry function
    result = await core_connector.submit_knowledge_entry(entry)
    return {"status": "ok", "module": "knowledge", "core_response": result}
