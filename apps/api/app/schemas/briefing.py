from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class BriefingListingItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rank: int
    listing_id: str
    title: str
    company: str
    location: Optional[str] = None
    match_score: Optional[int] = None
    deadline: Optional[str] = None


class BriefingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    status: str  # queued, processing, done, failed
    script: Optional[str] = None
    media_url: Optional[str] = None
    provider: Optional[str] = None
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    listings: List[BriefingListingItem] = []


class BriefingCreateResponse(BaseModel):
    briefing_id: str
    status: str
    message: str
