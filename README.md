# Flight AI Backend

FastAPI + LangServe scaffold to power a flight reservation agent.

## What you get
- **FastAPI** app with CORS and health check
- **LangServe** agent mounted at `/agent`
- Amadeus client skeleton (OAuth + endpoints)
- Trip persistence service (SQLModel)
- Off-topic **intent classification** with policy routing (in-scope, small-talk, out-of-scope)
- Docker compose for **Postgres** and **Redis**
- `.env.example` for all required secrets

## Quick start

```bash
# 1) Clone the repo and enter the folder
git clone git@github.com:ahmadalshawakri/Flights-Agent-AI.git
cd Flights-Agent-AI

# 2) Create env and install
python -m venv .venv && source .venv/bin/activate
pip install -e .   # or: pip install -r requirements.txt if you prefer

# 3) Copy env
cp .env.example .env
# fill AMADEUS and OPENAI keys

# 4) Start infra (optional)
docker compose up -d

# 5) Run API
uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000/docs and http://localhost:8000/health

### Test the agent (stubbed tools, classifier active)
```bash
curl -X POST http://localhost:8000/agent/invoke   -H "Content-Type: application/json"   -d '{"input":"Tell me a joke"}'
```

### Endpoints (to be completed with real logic)
- `POST /amadeus/search` → returns normalized offers (currently minimal mapping)
- `POST /amadeus/price`
- `POST /amadeus/create-order`
- `POST /trips/save` (create)
- `GET  /trips/list` (list)
- `DELETE /trips/{id}` (delete)

### Next steps
1. Wire **tools** in `app/agent/tools.py` to call `AmadeusClient`.
2. Fill out mapping logic in `/amadeus/search` for better card data.
3. Add Redis caching + rate limits.
4. Add `/reservations/*` endpoints if you want simulated bookings list.
5. Connect Next.js UI and start building cards + chat.

Happy building!
