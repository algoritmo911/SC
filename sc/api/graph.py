from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel, Field
from typing import Dict

from sc.services import ku_graph # Using __init__.py in services to simplify import
# from sc.api.knowledge import knowledge_units_db # For KU existence check, if needed

# If this is part of a larger FastAPI application, use APIRouter
# Otherwise, for standalone, use FastAPI()
# router = APIRouter()
app = FastAPI(title="Graph API") # Assuming standalone for now, or part of a main app.

class LinkRequest(BaseModel):
    from_ku_id: str
    to_ku_id: str
    weight: float = Field(..., ge=0.0, le=1.0, description="Link weight, typically between 0.0 and 1.0")

# @router.post("/link", status_code=201)
@app.post("/api/graph/link", status_code=201)
async def link_knowledge_units(link_request: LinkRequest):
    """
    Creates a directed link between two Knowledge Units with a specified weight.
    """
    # Optional: Check if KUs actually exist in the main KU database
    # This requires access to knowledge_units_db from sc.api.knowledge
    # For now, we assume IDs are valid and proceed to create the link.
    # if link_request.from_ku_id not in knowledge_units_db or \
    #    link_request.to_ku_id not in knowledge_units_db:
    #     missing_kus = []
    #     if link_request.from_ku_id not in knowledge_units_db:
    #         missing_kus.append(link_request.from_ku_id)
    #     if link_request.to_ku_id not in knowledge_units_db:
    #         missing_kus.append(link_request.to_ku_id)
    #     raise HTTPException(
    #         status_code=404,
    #         detail=f"One or more Knowledge Units not found: {', '.join(missing_kus)}. Cannot create link."
    #     )

    if link_request.from_ku_id == link_request.to_ku_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot link a Knowledge Unit to itself."
        )

    success = ku_graph.add_link(
        from_ku_id=link_request.from_ku_id,
        to_ku_id=link_request.to_ku_id,
        weight=link_request.weight
    )

    if not success:
        # This case is currently only hit if weight is invalid,
        # but Pydantic model validation should catch that first.
        # It could be used for other business logic failures in add_link.
        raise HTTPException(
            status_code=400,
            detail="Failed to create link. Ensure weight is valid and KUs are distinct."
        )

    return {
        "message": "Link created successfully",
        "from_ku_id": link_request.from_ku_id,
        "to_ku_id": link_request.to_ku_id,
        "weight": link_request.weight
    }

# @router.get("/links/{ku_id}")
@app.get("/api/graph/links/{ku_id}")
async def get_outgoing_links(ku_id: str):
    """
    Retrieves all outgoing links for a given Knowledge Unit.
    """
    # Optional: Check if KU exists
    # if ku_id not in knowledge_units_db:
    #     raise HTTPException(status_code=404, detail=f"Knowledge Unit with ID '{ku_id}' not found.")

    links = ku_graph.get_links_from(ku_id)
    if links is None: # KU might exist but have no outgoing links
        return {"ku_id": ku_id, "links": []}

    return {"ku_id": ku_id, "links": [{"to_ku_id": target_id, "weight": w} for target_id, w in links]}

# @router.get("/all_links")
@app.get("/api/graph/all_links")
async def get_all_graph_links():
    """
    Retrieves the entire KU graph.
    """
    return ku_graph.get_all_links()

# To run this API (example using uvicorn):
# uvicorn sc.api.graph:app --reload --port 8001
#
# Example POST request using curl:
# curl -X POST "http://127.0.0.1:8001/api/graph/link" \
# -H "Content-Type: application/json" \
# -d '{"from_ku_id": "ku_A", "to_ku_id": "ku_B", "weight": 0.85}'
#
# Example GET request for specific KU links:
# curl -X GET "http://127.0.0.1:8001/api/graph/links/ku_A"
#
# Example GET request for all links:
# curl -X GET "http://127.0.0.1:8001/api/graph/all_links"

# Note: If `knowledge.py` and `graph.py` are part of the same overall FastAPI application,
# you would typically use APIRouter for each and include them in a main app.py.
# For example, in a main.py:
# from fastapi import FastAPI
# from sc.api import knowledge, graph
#
# app = FastAPI()
# app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])
# app.include_router(graph.router, prefix="/api/graph", tags=["graph"])
#
# Then, `knowledge.app` and `graph.app` would be `knowledge.router` and `graph.router`.
# For now, they are independent FastAPI apps for simplicity.
