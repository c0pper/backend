from pydantic import BaseModel


class VenueCreate(BaseModel):
    name: str
    lat: float
    lng: float
    address: str


class VenueOut(BaseModel):
    id: int
    owner_id: int
    name: str
    lat: float
    lng: float
    address: str

    model_config = {"from_attributes": True}
