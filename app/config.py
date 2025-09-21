from pydantic_settings import BaseSettings
from typing import List
from pydantic import field_validator

class Settings(BaseSettings):
    AMADEUS_BASE_URL: str = "https://test.api.amadeus.com"
    AMADEUS_API_KEY: str
    AMADEUS_API_SECRET: str
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    OPENAI_API_KEY: str
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    AGENT_INTENT_THRESHOLD: float = 0.70
    AGENT_BACKEND_BASE: str = "http://localhost:8000"
    AGENT_HTTP_TIMEOUT: float = 45

    class Config:
        env_file = ".env"

settings = Settings()
