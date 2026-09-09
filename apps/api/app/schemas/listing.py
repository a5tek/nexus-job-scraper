from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class ListingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    company: str
    location: Optional[str] = None
    remote_ok: Optional[bool] = None
    stipend: Optional[str] = None
    required_skills: List[str] = []
    experience_level: Optional[str] = None
    deadline: Optional[date] = None
    created_at: datetime


class OpportunityFeedItem(BaseModel):
    """
    User-personalized opportunity item combining listing data,
    match score, justification explanation, and shortlist status.
    """
    id: str
    title: str
    company: str
    location: Optional[str] = None
    remote_ok: Optional[bool] = None
    stipend: Optional[str] = None
    required_skills: List[str] = []
    experience_level: Optional[str] = None
    deadline: Optional[date] = None
    match_score: Optional[int] = None
    match_explanation: Optional[str] = None
    is_saved: bool = False
    source_url: Optional[str] = None


class SemanticSearchRequest(BaseModel):
    query: str
    limit: int = 20
    remote_only: Optional[bool] = None
