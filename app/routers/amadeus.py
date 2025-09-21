from fastapi import APIRouter, HTTPException
from app.schemas import FlightSearchParams, PriceVerifyRequest, CreateOrderRequest, FlightSummary, Money, Leg, Segment
from app.services.amadeus_client import amadeus

router = APIRouter(prefix="/amadeus", tags=["amadeus"])

@router.get("/health")
async def health():
    return {"amadeus": "ready"}

def _normalize_offer(item: dict) -> FlightSummary:
    # Very light mapping for card display. You can refine later.
    itineraries = item.get("itineraries", [])
    def leg(i):
        if i >= len(itineraries):
            return None
        it = itineraries[i]
        segs = it.get("segments", [])
        segments = []
        for s in segs:
            segments.append(Segment(
                carrierCode=s.get("carrierCode"),
                flightNumber=s.get("number"),
                **{
                    "from": {"iata": s.get("departure", {}).get("iataCode"), "terminal": s.get("departure", {}).get("terminal")},
                    "to": {"iata": s.get("arrival", {}).get("iataCode"), "terminal": s.get("arrival", {}).get("terminal")},
                },
                depart=s.get("departure", {}).get("at"),
                arrive=s.get("arrival", {}).get("at"),
                aircraft=(s.get("aircraft") or {}).get("code"),
                cabin=(s.get("co2Emissions") or [{}])[0].get("cabin", None)  # placeholder if cabin not present
            ))
        return Leg(
            depart=segs[0].get("departure", {}).get("at") if segs else None,
            arrive=segs[-1].get("arrival", {}).get("at") if segs else None,
            duration=it.get("duration"),
            stops=max(len(segs)-1, 0),
            segments=segments
        )
    total = item.get("price", {}).get("total", "0.00")
    currency = item.get("price", {}).get("currency", "USD")
    adults = item.get("travelerPricings", [{}])
    n_adults = sum(1 for t in adults if t.get("travelerType") == "ADULT") or 1
    price_per_adult = f"{float(total)/max(n_adults,1):.2f}"

    return FlightSummary(
        id=item.get("id", ""),
        route={"from": item.get("source", None), "to": None},  # we will compute in UI from segments
        outbound=leg(0),
        inbound=leg(1),
        price=Money(amount=str(total), currency=currency),
        pricePerAdult=Money(amount=str(price_per_adult), currency=currency),
        validatingAirlines=item.get("validatingAirlineCodes"),
        baggage=None,
        raw=item
    )

@router.post("/search")
async def search(params: FlightSearchParams):
    try:
        raw = await amadeus.search_offers(params.dict(exclude_none=True))
        offers = [_normalize_offer(item) for item in raw.get("data", [])]
        return {
            "offers": [o.model_dump(by_alias=True) for o in offers],
            "meta": {"count": len(offers), "currency": params.currencyCode, "requestId": "na"}
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

@router.post("/price")
async def price(req: PriceVerifyRequest):
    body = {"data": {"type": "flight-offers-pricing", "flightOffers": [req.offer]}}
    try:
        res = await amadeus.price_offer(body)
        # You can map to the priced FlightSummary here if desired
        return {"pricedOffer": res.get("data"), "raw": res}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

@router.post("/create-order")
async def create_order(req: CreateOrderRequest):
    body = {"data": {"type": "flight-order", "flightOffers": [req.offer], "travelers": req.travelers}}
    try:
        res = await amadeus.create_order(body)
        # Return minimal normalized reservation
        return {
            "reservationId": res.get("data", {}).get("id", "resv_simulated"),
            "status": "simulated",
            "pnr": None,
            "offer": None,
            "travelers": req.travelers,
            "raw": res
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
