from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EventCreate(BaseModel):
    venue_id: int
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    tags: Optional[str] = None
    image_url: Optional[str] = None


class EventOut(BaseModel):
    id: int
    venue_id: int
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    tags: Optional[str] = None
    image_url: Optional[str] = None

    model_config = {"from_attributes": True}


class EventWithVenue(EventOut):
    venue_name: str
    distance: Optional[float] = None
