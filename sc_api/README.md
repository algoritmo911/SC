# SC API

This directory contains the FastAPI-based API for interacting with the SC (Symbiotic Cognitive) Core. It provides endpoints for managing knowledge, tokens, and users.

## Purpose of Endpoints

The API is structured into modules, each handling a specific domain:

*   **`/api/knowledge`**:
    *   `GET /api/knowledge`: (Placeholder) Intended to list or query knowledge entries. Currently returns a status message.
    *   `POST /api/knowledge`: Submits a new knowledge entry to the SC Core via the `core_connector.submit_knowledge_entry` function. Expects a JSON body representing the knowledge entry.
*   **`/api/tokens`**:
    *   `GET /api/tokens`: (Placeholder) Intended to retrieve information about tokens. Currently returns a status message.
    *   `POST /api/tokens`: Requests the SC Core to mint a new token for a given contribution ID via the `core_connector.mint_token_for_contribution` function. Expects a JSON body with a `contribution_id` field.
*   **`/api/users`**:
    *   `GET /api/users/{user_id}`: Retrieves user information from the SC Core for a specific `user_id` via the `core_connector.get_user_by_id` function.
    *   `POST /api/users`: (Placeholder) Intended to create a new user. Currently returns a status message and echoes the received data. Expects a JSON body representing the user data.

## Module Structure

The API is organized as follows:

*   `main.py`: The main FastAPI application file. It initializes the FastAPI app and includes the routers from the individual modules.
*   `knowledge.py`: Contains the API router and endpoint definitions for knowledge-related operations.
*   `tokens.py`: Contains the API router and endpoint definitions for token-related operations.
*   `users.py`: Contains the API router and endpoint definitions for user-related operations.
*   `core_connector.py`: Defines the interface (and currently, placeholder implementations) for functions that interact with the SC Core. API endpoints call functions from this module to perform their tasks.
*   `__init__.py`: Makes the `sc_api` directory a Python package.

## How to Extend the API

1.  **Define Core Logic (if new functionality):**
    *   If the new API endpoint needs to interact with the SC Core in a new way, first define the new function signature in `sc_api/core_connector.py`.
    *   Implement a placeholder or the actual logic for this function.

2.  **Add Endpoint to Module:**
    *   Identify the appropriate module for your new endpoint (e.g., `knowledge.py`, `tokens.py`, `users.py`). If a new domain is being introduced, you might need to create a new module file (e.g., `new_feature.py`).
    *   In the chosen module file, import any necessary dependencies (e.g., `APIRouter`, `Body`, `Path` from `fastapi`, and the `core_connector`).
    *   Define your new endpoint function using the appropriate HTTP method decorator (e.g., `@router.get("/new-path")`, `@router.post("/new-path")`).
    *   Implement the endpoint logic, which will typically involve:
        *   Accepting parameters (path parameters, query parameters, request body).
        *   Calling the relevant function from `sc_api/core_connector.py`.
        *   Returning a response.

3.  **Include Router (if new module):**
    *   If you created a new module file (e.g., `new_feature.py`), you need to include its router in `sc_api/main.py`.
    *   Import the router from your new module (e.g., `from sc_api import new_feature`).
    *   Include the router in the FastAPI app (e.g., `app.include_router(new_feature.router, prefix="/api")`).

4.  **Add Dependencies:**
    *   Ensure any new Python package dependencies are added to the project's requirements file (e.g., `requirements.txt`, not created in this task but generally important).

5.  **Documentation:**
    *   Update this `README.md` to reflect any new endpoints or changes in module structure.
    *   Ensure your endpoint functions have clear docstrings, as FastAPI uses these for the automatic OpenAPI documentation.

## Running the API and Viewing Documentation

To run this API (assuming you have FastAPI and Uvicorn installed):

```bash
pip install fastapi uvicorn
# Navigate to the directory containing the sc_api folder
cd ..
# (If your current directory is sc_api, move one level up to where main.py can be found as sc_api.main)
uvicorn sc_api.main:app --reload
```

Once the server is running, you can access the API:

*   **API Root:** `http://127.0.0.1:8000/`
*   **Swagger UI (Interactive API Documentation):** `http://127.0.0.1:8000/docs`
*   **ReDoc (Alternative API Documentation):** `http://127.0.0.1:8000/redoc`

The Swagger UI at `/docs` allows you to interactively explore the API endpoints, view their expected request bodies and responses, and even try them out.
