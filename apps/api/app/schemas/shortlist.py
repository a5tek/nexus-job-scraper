from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.listing import OpportunityFeedItem


class ShortlistItemResponse(BaseModel):
    id: str
    user_id: str
    listing_id: str
    created_at: datetime
    listing: OpportunityFeedItem
