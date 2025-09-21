from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from app.config import settings
from app.db.models import TripModel, ReservationModel
from app.routers import amadeus as amadeus_router, trips as trips_router

# LangServe
from langserve import add_routes
from app.agent.router import EntryRouter as AgentRouter


print("CORS:", settings.CORS_ORIGINS)

app = FastAPI(title="Flight AI API", version="0.1.0")

cors = settings.CORS_ORIGINS
allow_creds = not (len(cors) == 1 and cors[0] == "*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors,
    allow_credentials=allow_creds,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup (simple dev behavior)
@app.on_event("startup")
def on_startup():
    from app.deps import engine
    SQLModel.metadata.create_all(engine)

# Routers
app.include_router(amadeus_router.router)
app.include_router(trips_router.router)

# Agent (LangServe)
add_routes(app, AgentRouter, path="/agent")

@app.get("/health")
def health():
    return {"ok": True, "ts": "2025-09-19T11:24:59.115514Z"}
