# sc/models.py
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class KnowledgeUnit(BaseModel):
    id: str
    author_id: str
    content_text: Optional[str]
    content_audio_url: Optional[str]
    content_video_url: Optional[str]
    vr_scene_url: Optional[str]
    ar_assets: Optional[List[str]]
    tags: Optional[List[str]] = []
    created_at: datetime
    pov_score: Optional[float] = 0.0
    moderation_status: Optional[str] = "pending"
