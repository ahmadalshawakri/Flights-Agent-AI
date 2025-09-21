from pydantic import BaseModel, Field
from typing import Optional, List, Any

class FlightSearchParams(BaseModel):
    originLocationCode: str
    destinationLocationCode: str
    departureDate: str
    returnDate: Optional[str] = None
    adults: int = 1
    children: Optional[int] = 0
    infants: Optional[int] = 0
    travelClass: Optional[str] = None  # ECONOMY | PREMIUM_ECONOMY | BUSINESS | FIRST
    currencyCode: Optional[str] = "USD"
    nonStop: Optional[bool] = False
    max: Optional[int] = 20

class Money(BaseModel):
    amount: str
    currency: str

class Segment(BaseModel):
    carrierCode: Optional[str] = None
    flightNumber: Optional[str] = None
    from_: dict = Field(default_factory=dict, alias="from")
    to: dict = Field(default_factory=dict)
    depart: Optional[str] = None
    arrive: Optional[str] = None
    aircraft: Optional[str] = None
    cabin: Optional[str] = None

class Leg(BaseModel):
    depart: Optional[str] = None
    arrive: Optional[str] = None
    duration: Optional[str] = None
    stops: Optional[int] = None
    segments: List[Segment] = Field(default_factory=list)

class FlightSummary(BaseModel):
    id: str
    route: dict
    outbound: Optional[Leg] = None
    inbound: Optional[Leg] = None
    price: Money
    pricePerAdult: Optional[Money] = None
    validatingAirlines: Optional[List[str]] = None
    baggage: Optional[dict] = None
    raw: Any

class PriceVerifyRequest(BaseModel):
    offer: Any

class CreateOrderRequest(BaseModel):
    offer: Any
    travelers: List[Any]
    testMode: Optional[bool] = True
    idempotencyKey: Optional[str] = None

class SaveTripRequest(BaseModel):
    offerId: str
    offer: Any
    note: Optional[str] = None
