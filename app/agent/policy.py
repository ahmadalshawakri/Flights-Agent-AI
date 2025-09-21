from typing import Dict, List
from app.config import settings
from .intents import IntentResult

SUGGESTIONS = [
    "Search AMM → DOH on Oct 10",
    "Show my saved trips",
    "Reserve the cheapest AMM → DOH"
]

def apply_policy(ir: IntentResult) -> Dict:
    threshold = settings.AGENT_INTENT_THRESHOLD
    in_scope = ir.intent in {
        "FLIGHT_SEARCH", "PRICE_VERIFY", "CREATE_ORDER",
        "SAVE_TRIP", "LIST_TRIPS", "CANCEL_RESERVATION"
    }
    out_of_scope = (not in_scope) or (ir.confidence < threshold)
    small_talk = (ir.intent == "SMALL_TALK")
    return {
        "intent": ir.intent,
        "confidence": ir.confidence,
        "outOfScope": out_of_scope and not small_talk,
        "smallTalk": small_talk,
        "suggestions": SUGGESTIONS
    }
