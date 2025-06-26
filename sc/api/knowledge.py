from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, List, Any
import time
from collections import defaultdict

from sc.models import KnowledgeUnit
from sc.services.ku_generator import generate_ku_from_prompt
from sc.services.flowshield import is_under_attack

# Initialize FastAPI app
# This will be a sub-application if there's a main app.py,
# or it can be run directly for this specific API.
# For now, let's assume it's part of a larger structure.
# We can use APIRouter if we combine it later.
# from fastapi import APIRouter
# router = APIRouter()

app = FastAPI(title="Knowledge API") # If running standalone for now

# In-memory storage for Knowledge Units
knowledge_units_db: Dict[str, KnowledgeUnit] = {}

# In-memory tracker for request counts per IP for rate limiting
# {ip: [timestamp1, timestamp2, ...]}
# A more robust solution would use Redis or a similar persistent store.
rate_tracker: Dict[str, List[float]] = defaultdict(list)
REQUEST_WINDOW_SECONDS = 60  # Track requests over a 60-second window
MAX_REQUESTS_IN_WINDOW_API = 50 # Specific threshold for this API endpoint

class KUDefinition(BaseModel):
    prompt: str
    context: Dict[str, Any] = {}


def get_request_count_for_ip(ip: str) -> int:
    """
    Counts recent requests for a given IP within the REQUEST_WINDOW_SECONDS.
    """
    current_time = time.time()
    # Filter out timestamps older than the window
    rate_tracker[ip] = [t for t in rate_tracker[ip] if current_time - t < REQUEST_WINDOW_SECONDS]
    return len(rate_tracker[ip])

def record_request_for_ip(ip: str):
    """
    Records the current request timestamp for the given IP.
    """
    rate_tracker[ip].append(time.time())

# @router.post("/units", response_model=KnowledgeUnit, status_code=201)
@app.post("/api/knowledge/units", response_model=KnowledgeUnit, status_code=201)
async def create_knowledge_unit(definition: KUDefinition, request: Request):
    """
    Creates a new Knowledge Unit based on a prompt and context.
    Applies rate limiting before processing.
    """
    client_ip = request.client.host if request.client else "unknown"

    # Rate Limiting Check
    current_request_count = get_request_count_for_ip(client_ip)

    # Using MAX_REQUESTS_IN_WINDOW_API for this specific endpoint,
    # flowshield's internal MAX_REQUESTS_PER_WINDOW can be a global default or for other services.
    if is_under_attack(ip=client_ip, request_count=current_request_count + 1): # Check with current request included
        # Update rate_tracker even for denied request to ensure persistent attackers are blocked
        record_request_for_ip(client_ip)
        raise HTTPException(
            status_code=429,
            detail=f"Too many requests from {client_ip}. Please try again later. Limit: {MAX_REQUESTS_PER_WINDOW} per {REQUEST_WINDOW_SECONDS}s."
        )

    record_request_for_ip(client_ip)

    # Generate KU
    try:
        ku = generate_ku_from_prompt(prompt=definition.prompt, context=definition.context)
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=500, detail=f"Failed to generate Knowledge Unit: {str(e)}")

    # Store KU (in-memory)
    if ku.id in knowledge_units_db:
        # This should ideally not happen if IDs are truly unique UUIDs
        raise HTTPException(status_code=500, detail=f"Duplicate KU ID generated: {ku.id}. Please try again.")

    knowledge_units_db[ku.id] = ku

    return ku

# @router.get("/units/{ku_id}", response_model=KnowledgeUnit)
@app.get("/api/knowledge/units/{ku_id}", response_model=KnowledgeUnit)
async def get_knowledge_unit(ku_id: str, request: Request):
    """
    Retrieves a specific Knowledge Unit by its ID.
    """
    client_ip = request.client.host if request.client else "unknown"
    # Optionally, apply rate limiting to GET requests too
    # current_request_count = get_request_count_for_ip(client_ip)
    # if is_under_attack(ip=client_ip, request_count=current_request_count + 1):
    #     record_request_for_ip(client_ip)
    #     raise HTTPException(status_code=429, detail="Too many requests.")
    # record_request_for_ip(client_ip)

    if ku_id not in knowledge_units_db:
        raise HTTPException(status_code=404, detail=f"Knowledge Unit with ID '{ku_id}' not found.")
    return knowledge_units_db[ku_id]

# To run this API (example using uvicorn):
# uvicorn sc.api.knowledge:app --reload --port 8000
#
# Example POST request using curl:
# curl -X POST "http://127.0.0.1:8000/api/knowledge/units" \
# -H "Content-Type: application/json" \
# -d '{"prompt": "Describe a futuristic city", "context": {"year": 2242}}'
#
# Example GET request using curl:
# curl -X GET "http://127.0.0.1:8000/api/knowledge/units/{ku_id_from_post_response}"

# For simplicity, the `is_under_attack` function in `flowshield` uses its own
# MAX_REQUESTS_PER_WINDOW. Here, we are managing the window and count explicitly
# in the API layer. We could also pass MAX_REQUESTS_IN_WINDOW_API to `is_under_attack`
# if we wanted `flowshield` to be more configurable per call.
# The current `is_under_attack` in `flowshield.py` uses `MAX_REQUESTS_PER_WINDOW = 100`.
# Let's adjust the API's specific limit for demonstration.
# The `is_under_attack` function will use its own threshold.
# To make it consistent, let's ensure `flowshield.is_under_attack` uses the API's desired threshold.

# Re-thinking the flowshield integration:
# The task: "Перед каждым созданием KU — делай проверку: if is_under_attack(ip=request.client.host, request_count=rate_tracker[ip]):"
# This implies `rate_tracker` is managed here, and its current state (count) is passed to `is_under_attack`.
# `is_under_attack` then just compares this count to its internal threshold.

# Let's refine the rate limiting logic in `create_knowledge_unit` to match the request precisely.
# The `rate_tracker` will be the one from the task description.
# `flowshield.MAX_REQUESTS_PER_WINDOW` will be the authority for the threshold.

# Redefining rate_tracker to be simpler as per task: {ip: count}
# This requires a mechanism to reset counts periodically.
# The previous approach (list of timestamps) is more robust for sliding windows.
# Let's stick to the timestamp list for `rate_tracker` as it's more common,
# and `get_request_count_for_ip` provides the count for `is_under_attack`.
# The `is_under_attack` function's `MAX_REQUESTS_PER_WINDOW` will be the effective limit.
# The `MAX_REQUESTS_IN_WINDOW_API` in this file is redundant if `flowshield` has its own fixed limit.
# For clarity and to match the prompt, `is_under_attack` will use its own `MAX_REQUESTS_PER_WINDOW`.
# The `knowledge.py` will manage the window and count calculation.

# The current `is_under_attack` function is:
# def is_under_attack(ip: str, request_count: int) -> bool:
# if request_count > MAX_REQUESTS_PER_WINDOW: # MAX_REQUESTS_PER_WINDOW = 100 in flowshield
# return True
# return False

# So, the call: is_under_attack(ip=client_ip, request_count=current_request_count + 1)
# will compare (current_request_count + 1) against flowshield's MAX_REQUESTS_PER_WINDOW (100).
# This seems correct according to the task.
# The `REQUEST_WINDOW_SECONDS` (60s) is defined here and used to calculate `current_request_count`.
# This setup is fine.
