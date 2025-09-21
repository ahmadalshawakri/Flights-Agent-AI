import os
from app.config import settings
from pydantic import BaseModel, Field
from typing import Literal
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

os.environ.setdefault("OPENAI_API_KEY", settings.OPENAI_API_KEY)

IntentType = Literal[
    "FLIGHT_SEARCH", "PRICE_VERIFY", "CREATE_ORDER",
    "SAVE_TRIP", "LIST_TRIPS", "CANCEL_RESERVATION",
    "HELP", "SMALL_TALK", "OUT_OF_SCOPE"
]

class IntentResult(BaseModel):
    intent: IntentType
    confidence: float = Field(ge=0, le=1)

INTENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are an intent classifier for a flight reservation assistant. "
     "Allowed intents: FLIGHT_SEARCH, PRICE_VERIFY, CREATE_ORDER, SAVE_TRIP, "
     "LIST_TRIPS, CANCEL_RESERVATION, HELP, SMALL_TALK, OUT_OF_SCOPE. "
     "Return JSON with intent and confidence (0-1). Be conservative."),
    ("human", "{user_input}")
])

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
classifier = INTENT_PROMPT | llm.with_structured_output(IntentResult)
