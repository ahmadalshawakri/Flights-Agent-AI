import time, httpx
from tenacity import retry, wait_exponential, stop_after_attempt
from app.config import settings

class AmadeusClient:
    def __init__(self):
        self._token = None
        self._exp = 0

    @retry(wait=wait_exponential(min=1, max=8), stop=stop_after_attempt(3))
    async def _get_token(self) -> str:
        if self._token and time.time() < self._exp - 30:
            return self._token
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{settings.AMADEUS_BASE_URL}/v1/security/oauth2/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": settings.AMADEUS_API_KEY,
                    "client_secret": settings.AMADEUS_API_SECRET,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30.0,
            )
        r.raise_for_status()
        data = r.json()
        self._token = data["access_token"]
        self._exp = time.time() + int(data["expires_in"])
        return self._token

    async def _headers(self):
        token = await self._get_token()
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async def search_offers(self, params: dict):
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{settings.AMADEUS_BASE_URL}/v2/shopping/flight-offers",
                params=params,
                headers=await self._headers(),
                timeout=30.0,
            )
        r.raise_for_status()
        return r.json()

    async def price_offer(self, body: dict):
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{settings.AMADEUS_BASE_URL}/v1/shopping/flight-offers/pricing",
                json=body,
                headers=await self._headers(),
                timeout=30.0,
            )
        r.raise_for_status()
        return r.json()

    async def create_order(self, body: dict):
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{settings.AMADEUS_BASE_URL}/v1/booking/flight-orders",
                json=body,
                headers=await self._headers(),
                timeout=30.0,
            )
        r.raise_for_status()
        return r.json()

amadeus = AmadeusClient()
