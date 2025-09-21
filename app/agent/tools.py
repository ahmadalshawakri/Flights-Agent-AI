from __future__ import annotations

import os
from typing import Optional, Literal

import httpx
from pydantic import BaseModel, Field, model_validator
from langchain.tools import tool

# Where the FastAPI backend is running (the same app that exposes /amadeus/*)
BASE = os.getenv("AGENT_BACKEND_BASE", "http://127.0.0.1:8000")
TIMEOUT = float(os.getenv("AGENT_HTTP_TIMEOUT", "45.0"))


def _post(path: str, json: dict) -> dict:
    """POST to our backend and return JSON. Never raise to avoid 500s from the agent path."""
    url = f"{BASE.rstrip('/')}{path}"
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            r = client.post(url, json=json)
            r.raise_for_status()
            return r.json()
    except httpx.HTTPStatusError as e:
        return {
            "error": "UPSTREAM_HTTP_ERROR",
            "status": e.response.status_code,
            "endpoint": url,
            "body": json,
            "detail": _safe_json(e.response),
        }
    except httpx.RequestError as e:
        return {
            "error": "NETWORK_ERROR",
            "endpoint": url,
            "body": json,
            "detail": str(e),
        }

def _safe_json(resp: httpx.Response) -> dict | str:
    try:
        return resp.json()
    except Exception:
        return resp.text

class SearchOffersArgs(BaseModel):
    originLocationCode: str = Field(..., description="Origin IATA code, e.g. AMM")
    destinationLocationCode: str = Field(..., description="Destination IATA code, e.g. DOH")
    departureDate: str = Field(..., description="YYYY-MM-DD")
    returnDate: Optional[str] = Field(None, description="YYYY-MM-DD (round-trip)")
    adults: int = 1
    children: int = 0
    infants: int = 0
    travelClass: Optional[Literal["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"]] = None
    nonStop: bool = False
    currencyCode: str = "USD"
    max: int = 10

@tool("search_offers", args_schema=SearchOffersArgs)
def search_offers_tool(**kwargs) -> dict:
    """
    Search flight offers (Amadeus Flight Offers Search).
    Calls our backend: POST /amadeus/search with the same JSON body.
    """
    return _post("/amadeus/search", kwargs)

class PriceOfferArgs(BaseModel):
    # Support either an Amadeus offer id OR the raw offer object, plus optional currency override.
    offerId: Optional[str] = Field(
        None, description="ID of the offer returned by /amadeus/search"
    )
    offer: Optional[dict] = Field(
        None, description="Raw offer object returned by Amadeus search"
    )
    currencyCode: Optional[str] = Field(
        None, description="If provided, backend may re-price to this currency"
    )

    @model_validator(mode="after")
    def _must_have_one(self):
        if not (self.offerId or self.offer):
            raise ValueError("Provide either offerId or offer")
        return self


@tool("price_offer", args_schema=PriceOfferArgs)
def price_offer_tool(**kwargs) -> dict:
    """
    Verify pricing for a selected offer (Amadeus Flight Offers Price).
    Calls our backend: POST /amadeus/price with the same JSON body.
    """
    return _post("/amadeus/price", kwargs)

class CreateOrderArgs(BaseModel):
    # Minimal inputs; your backend can accept either an offerId or the raw offer + traveler details.
    offerId: Optional[str] = Field(
        None, description="ID of the priced offer to purchase"
    )
    offer: Optional[dict] = Field(
        None, description="Raw priced offer object from Amadeus"
    )
    travelers: list[dict] = Field(
        ..., description="Traveler list per Amadeus schema (name, DOB, gender, docs, contacts)"
    )
    # Optional contact/payment data depending on how your backend is implemented.
    contacts: Optional[dict] = None
    payment: Optional[dict] = None

    @model_validator(mode="after")
    def _have_offer(self):
        if not (self.offerId or self.offer):
            raise ValueError("Provide either offerId or offer")
        return self


@tool("create_order", args_schema=CreateOrderArgs)
def create_order_tool(**kwargs) -> dict:
    """
    Create a (sandbox) flight order (Amadeus Flight Create Orders).
    Calls our backend: POST /amadeus/create-order with the same JSON body.
    """
    return _post("/amadeus/create-order", kwargs)
