from typing import Optional, Any
from sqlmodel import SQLModel, Field
from datetime import datetime
from sqlalchemy import Column, JSON

class TripModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    offer_id: str
    data: dict = Field(sa_column=Column(JSON))
    note: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ReservationModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    reservation_id: str
    status: str
    pnr: Optional[str] = None
    offer: dict = Field(sa_column=Column(JSON))
    travelers: Optional[list] = Field(
        default=None, sa_column=Column(JSON)
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
