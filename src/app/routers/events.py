from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.venue import Venue
from app.models.event import Event
from app.schemas.event import EventCreate, EventOut, EventWithVenue
from app.dependencies import get_current_user, require_venue_owner

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_event(
    body: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_venue_owner),
):
    venue = db.query(Venue).filter(Venue.id == body.venue_id).first()
    if not venue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venue not found")
    if venue.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your venue")
    event = Event(
        venue_id=body.venue_id,
        title=body.title,
        description=body.description,
        start_time=body.start_time,
        end_time=body.end_time,
        tags=body.tags,
        image_url=body.image_url,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/", response_model=List[EventWithVenue])
def list_events(
    venue_id: Optional[int] = Query(None),
    owner_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Event, Venue.name.label("venue_name")).join(
        Venue, Event.venue_id == Venue.id
    )
    if venue_id is not None:
        query = query.filter(Event.venue_id == venue_id)
    if owner_id is not None:
        query = query.filter(Venue.owner_id == owner_id)
    results = query.all()
    return [
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
        )
        for event, venue_name in results
    ]


@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_venue_owner),
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    venue = db.query(Venue).filter(Venue.id == event.venue_id).first()
    if venue.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your venue")
    db.delete(event)
    db.commit()
