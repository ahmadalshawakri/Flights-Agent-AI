from typing import Dict
from langchain_core.runnables import RunnableLambda, RunnableBranch
from .intents import classifier, IntentResult
from .policy import apply_policy
from .responders import OutOfScopeResponder, SmallTalkResponder
from .chain import build_agent

def _classify(payload: Dict) -> Dict:
    ir: IntentResult = classifier.invoke({"user_input": payload["input"]})
    ctx = apply_policy(ir)
    # keep input + policy context
    return {"input": payload["input"], "context": ctx}

def _is_out_of_scope(x: Dict) -> bool:
    return x.get("context", {}).get("outOfScope") is True

def _is_small_talk(x: Dict) -> bool:
    return x.get("context", {}).get("smallTalk") is True

# --- wrap the agent so it's a Runnable ---
ToolAgent = build_agent()
def _run_tool_agent(state: Dict) -> Dict:
    try:
        res = ToolAgent.invoke({"input": state["input"]})
    except Exception as e:
        # graceful response instead of 500
        return {
            "output": "I couldn't extract enough info to search flights. "
                      "Please provide origin (IATA), destination (IATA), and departure date (YYYY-MM-DD).",
            "context": state.get("context", {}),
            "error": str(e)[:200],
            "suggestions": [
                "Search AMM → DOH on 2025-10-10",
                "Search AMM → DXB on 2025-11-05 (return 2025-11-10)",
            ],
        }
    out = {"context": state.get("context", {})}
    if isinstance(res, dict):
        out.update(res)
        out.setdefault("output", res.get("output") or res.get("text") or "")
    else:
        out["output"] = str(res)
    return out

ToolAgentRunnable = RunnableLambda(_run_tool_agent)

# build the router: classify → branch → (selected runnable)
Classifier = RunnableLambda(_classify)

Branch = RunnableBranch(
    (_is_out_of_scope, OutOfScopeResponder),
    (_is_small_talk, SmallTalkResponder),
    ToolAgentRunnable,
)

# optional: final normalizer (safe no-op now since we keep context)
def _normalize_output(result: Dict) -> Dict:
    if "context" not in result:
        result["context"] = {}
    if "output" not in result:
        result["output"] = ""
    return result

Router = Classifier | Branch | RunnableLambda(_normalize_output)

def _adapt_in(x):
    # If client already sent {"input": "..."} keep it
    if isinstance(x, dict) and "input" in x:
        return x
    # Otherwise, treat body as the raw user text
    return {"input": x}

EntryRouter = RunnableLambda(_adapt_in) | Router
