from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
from enum import Enum
import uuid

class ModerationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class KnowledgeUnit(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    author_id: str
    content_text: str
    content_audio_url: Optional[str] = None
    content_video_url: Optional[str] = None
    vr_scene_url: Optional[str] = None
    ar_assets: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    pov_score: float = 0.0
    moderation_status: ModerationStatus = ModerationStatus.PENDING
    version_history: List[str] = Field(default_factory=list) # List of previous KnowledgeUnit IDs or version hashes

    class Config:
        use_enum_values = True # Ensures that enum values are used in serialization
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
        # Example for OpenAPI documentation, if needed
        # schema_extra = {
        #     "example": {
        #         "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
        #         "author_id": "user_123",
        #         "content_text": "This is a detailed explanation of a complex topic.",
        #         "vr_scene_url": "ipfs://Qm...",
        #         "ar_assets": ["ipfs://Qm...", "ipfs://Qm..."],
        #         "tags": ["science", "technology", "education"],
        #         "created_at": "2024-07-15T10:30:00Z",
        #         "updated_at": "2024-07-15T10:30:00Z",
        #         "pov_score": 0.85,
        #         "moderation_status": "approved",
        #         "version_history": []
        #     }
        # }
