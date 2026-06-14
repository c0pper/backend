from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.event import Event
from app.models.venue import Venue
from app.schemas.event import EventWithVenue

router = APIRouter(prefix="/feed", tags=["feed"])


@router.get("/", response_model=List[EventWithVenue])
def get_feed(
    lat: float = Query(...),
    lng: float = Query(...),
    radius: float = Query(5.0),
    db: Session = Depends(get_db),
):
    distance_expr = func.ST_DistanceSphere(
        func.ST_SetSRID(func.ST_MakePoint(Venue.lng, Venue.lat), 4326),
        func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326),
    )

    rows = (
        db.query(Event, Venue.name.label("venue_name"), (distance_expr / 1000).label("distance"))
        .join(Venue, Event.venue_id == Venue.id)
        .filter(distance_expr <= radius * 1000)
        .order_by(Event.start_time.asc())
        .all()
    )

    results = []
    for event, venue_name, dist in rows:
        results.append(
            EventWithVenue(
                id=event.id,
                venue_id=event.venue_id,
                title=event.title,
                description=event.description,
                start_time=event.start_time,
                end_time=event.end_time,
                tags=event.tags,
                image_url=event.image_url,
                venue_name=venue_name,
                distance=round(dist, 2),
            )
        )
    return results
