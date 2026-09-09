from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    file_name: str
    file_url: str
    extracted_text: Optional[str] = None
    content_hash: Optional[str] = None
    processing_status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ResumeStatusResponse(BaseModel):
    id: str
    processing_status: str  # uploaded, reading, understanding, matching, ready, failed
    is_active: bool
    error_message: Optional[str] = None
    matches_calculated: int = 0
