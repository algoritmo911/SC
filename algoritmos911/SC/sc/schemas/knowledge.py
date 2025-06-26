from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class KnowledgeUnitBase(BaseModel):
    author_id: str
    content_text: Optional[str] = None
    content_audio_url: Optional[str] = None
    content_video_url: Optional[str] = None
    vr_scene_url: Optional[str] = None
    ar_assets: Optional[List[str]] = Field(default_factory=list)
    tags: Optional[List[str]] = Field(default_factory=list)

class KnowledgeUnitCreate(KnowledgeUnitBase):
    pass

class KnowledgeUnitResponse(KnowledgeUnitBase):
    id: str
    created_at: datetime
    pov_score: Optional[float] = 0.0
    moderation_status: Optional[str] = "pending"

    class Config:
        orm_mode = True # or from_attributes = True for Pydantic v2
