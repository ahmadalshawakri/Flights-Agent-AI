from sqlmodel import Session, select
from app.db.models import TripModel

class TripsService:
    def save(self, session: Session, offer_id: str, data: dict, note: str | None = None):
        trip = TripModel(offer_id=offer_id, data=data, note=note)
        session.add(trip)
        session.commit()
        session.refresh(trip)
        return trip

    def list(self, session: Session, page: int = 1, page_size: int = 20):
        stmt = select(TripModel).offset((page-1)*page_size).limit(page_size)
        rows = session.exec(stmt).all()
        return rows

    def delete(self, session: Session, trip_id: int) -> bool:
        trip = session.get(TripModel, trip_id)
        if not trip:
            return False
        session.delete(trip)
        session.commit()
        return True

trips_service = TripsService()
