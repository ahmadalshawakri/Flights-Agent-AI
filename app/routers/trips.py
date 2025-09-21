from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas import SaveTripRequest
from app.services.trips_service import trips_service
from app.deps import get_session

router = APIRouter(prefix="/trips", tags=["trips"])

@router.get("/health")
async def health():
    return {"trips": "ready"}

@router.post("/save", status_code=201)
def save_trip(req: SaveTripRequest, session = Depends(get_session)):
    trip = trips_service.save(session, req.offerId, req.offer, req.note)
    return {"tripId": f"trip_{trip.id}", "createdAt": trip.created_at.isoformat() + "Z"}

@router.get("/list")
def list_trips(page: int = Query(1, ge=1), pageSize: int = Query(20, ge=1, le=100), session = Depends(get_session)):
    rows = trips_service.list(session, page, pageSize)
    return {
        "trips": [
            {
                "tripId": f"trip_{r.id}",
                "offerId": r.offer_id,
                "summary": None,
                "note": r.note,
                "createdAt": r.created_at.isoformat() + "Z"
            } for r in rows
        ],
        "meta": {"page": page, "pageSize": pageSize, "total": len(rows)}
    }

@router.delete("/{trip_id}")
def delete_trip(trip_id: int, session = Depends(get_session)):
    ok = trips_service.delete(session, trip_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True}
