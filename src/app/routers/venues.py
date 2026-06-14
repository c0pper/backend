from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.user import User
from app.models.venue import Venue
from app.models.event import Event
from app.schemas.venue import VenueCreate, VenueOut
from app.dependencies import get_current_user, require_venue_owner

router = APIRouter(prefix="/venues", tags=["venues"])


@router.post("/", response_model=VenueOut, status_code=status.HTTP_201_CREATED)
def create_venue(
    body: VenueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_venue_owner),
):
    venue = Venue(
        owner_id=current_user.id,
        name=body.name,
        lat=body.lat,
        lng=body.lng,
        address=body.address,
    )
    db.add(venue)
    db.commit()
    db.refresh(venue)
    return venue


@router.get("/{venue_id}", response_model=VenueOut)
def get_venue(venue_id: int, db: Session = Depends(get_db)):
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venue not found")
    return venue


@router.get("/", response_model=List[VenueOut])
def list_venues(
    owner_id: int = None,
    lat: float = None,
    lng: float = None,
    radius: float = None,
    db: Session = Depends(get_db),
):
    query = db.query(Venue)
    if owner_id is not None:
        query = query.filter(Venue.owner_id == owner_id)
    if lat is not None and lng is not None and radius is not None:
        user_point = func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326)
        venue_point = func.ST_SetSRID(func.ST_MakePoint(Venue.lng, Venue.lat), 4326)
        query = query.filter(func.ST_DWithin(venue_point, user_point, radius * 1000))
    return query.all()


@router.delete("/{venue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_venue(
    venue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_venue_owner),
):
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venue not found")
    if venue.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your venue")
    db.query(Event).filter(Event.venue_id == venue_id).delete()
    db.delete(venue)
    db.commit()
