from fastapi import FastAPI
import logging
import sys

# --- Logging Configuration ---
# Configure basic logging
# In a production app, you might use a more sophisticated setup,
# e.g., structured logging, log rotation, sending logs to a centralized service.
logging.basicConfig(
    level=logging.INFO, # Set the default logging level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout) # Log to stdout
    ]
)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Sentient Concord (SC) API",
    description="API for managing KnowledgeUnits, VR/AR experiences, and more.",
    version="0.1.0"
)

@app.on_event("startup")
async def startup_event():
    logger.info("SC API application startup complete.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("SC API application shutdown.")


@app.get("/")
async def root():
    logger.info("Root endpoint '/' was called.")
    return {"message": "Welcome to the SC API"}

# Further routers will be included here
from .api import knowledge # Make sure this import is correct based on your structure
app.include_router(knowledge.router, prefix="/api", tags=["Knowledge Units"])
