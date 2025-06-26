# sc/api/knowledge.py
from fastapi import APIRouter, UploadFile, File, Form
from uuid import uuid4
from datetime import datetime
from sc.models import KnowledgeUnit

router = APIRouter()

@router.post("/upload_vr")
async def upload_vr_scene(
    author_id: str = Form(...),
    tags: str = Form(...),
    vr_scene: UploadFile = File(...)
):
    # Симулируем загрузку в IPFS
    ipfs_hash = f"QmFakeHash{uuid4().hex[:6]}"
    ku = KnowledgeUnit(
        id=str(uuid4()),
        author_id=author_id,
        content_text=None,
        vr_scene_url=f"ipfs://{ipfs_hash}",
        tags=tags.split(","),
        created_at=datetime.utcnow()
    )
    # Временно просто возвращаем KU
    return {"status": "ok", "data": ku}
