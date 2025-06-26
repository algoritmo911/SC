from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Body
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging
from datetime import datetime, timezone


from ..models import KnowledgeUnit, ModerationStatus
from ..services import ipfs_service
from ..db import memory_db
import uuid # For generating IDs if not done by model default_factory in some cases

router = APIRouter()
logger = logging.getLogger(__name__)

# --- Request Models ---
class KnowledgeUnitMetadata(BaseModel):
    content_text: str
    tags: Optional[List[str]] = Field(default_factory=list)
    # Add any other metadata fields that are expected from the client
    # For example, if author_id is not from JWT, it could be here.
    # For now, assuming author_id will come from JWT/authentication.

class UploadVRResponse(BaseModel):
    status: str
    id: str
    ipfs_hash: str # Included for clarity in response, though vr_scene_url has it
    vr_scene_url: str

# --- Utility for JWT (Mocked for now) ---
# In a real app, this would come from an authentication dependency
async def get_current_user_author_id() -> str:
    """Mocked function to get current user's author_id."""
    return "mock_author_123"


@router.post("/knowledge/upload_vr", response_model=UploadVRResponse, status_code=201)
async def upload_vr_scene(
    vr_scene: UploadFile = File(..., description="The VR scene file (e.g., .gltf, .usdz)"),
    content_text: str = Form(..., description="Textual content/description of the Knowledge Unit."),
    tags: Optional[List[str]] = Form(None, description="A list of tags for the Knowledge Unit."),
    author_id: str = Depends(get_current_user_author_id) # Simulate getting author_id from JWT
):
    """
    Uploads a VR scene and associated metadata to create a new Knowledge Unit.

    - **vr_scene**: The VR scene file itself.
    - **content_text**: The main textual description for this knowledge unit.
    - **tags**: Optional list of tags.
    """
    logger.info(f"Received VR scene upload request for author: {author_id}")

    if not vr_scene.filename:
        raise HTTPException(status_code=400, detail="VR scene file name is missing.")

    # Basic validation for file type could be added here based on filename extension
    # e.g., if not vr_scene.filename.endswith(('.gltf', '.usdz')):
    # raise HTTPException(status_code=400, detail="Invalid file type for VR scene.")

    try:
        # 1. Upload VR scene to IPFS (mocked)
        ipfs_hash = await ipfs_service.mock_upload_to_ipfs(vr_scene)
        vr_scene_url = f"ipfs://{ipfs_hash}"
        logger.info(f"VR scene uploaded to mock IPFS. Hash: {ipfs_hash}")

        # 2. Create KnowledgeUnit
        # Ensure tags are handled correctly if None
        processed_tags = tags if tags is not None else []


        ku = KnowledgeUnit(
            author_id=author_id,
            content_text=content_text,
            vr_scene_url=vr_scene_url,
            tags=processed_tags,
            # Other fields will use defaults from Pydantic model
            # pov_score, moderation_status, version_history etc.
            created_at=datetime.now(timezone.utc), # Explicitly set for clarity
            updated_at=datetime.now(timezone.utc)  # Explicitly set for clarity
        )

        # 3. Save KnowledgeUnit to DB (in-memory)
        saved_ku = memory_db.save_knowledge_unit(ku)
        logger.info(f"KnowledgeUnit created and saved. ID: {saved_ku.id}")

        return UploadVRResponse(
            status="success",
            id=saved_ku.id,
            ipfs_hash=ipfs_hash, # For client convenience
            vr_scene_url=saved_ku.vr_scene_url
        )

    except Exception as e:
        logger.error(f"Error during VR scene upload: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error during VR scene upload: {str(e)}")


@router.get("/knowledge/{ku_id}", response_model=KnowledgeUnit)
async def get_knowledge_unit(ku_id: str):
    """
    Retrieves a specific Knowledge Unit by its ID.
    """
    ku = memory_db.get_knowledge_unit_by_id(ku_id)
    if not ku:
        raise HTTPException(status_code=404, detail="Knowledge Unit not found")
    return ku

@router.get("/knowledge", response_model=List[KnowledgeUnit])
async def list_knowledge_units():
    """
    Lists all available Knowledge Units.
    """
    return memory_db.get_all_knowledge_units()
