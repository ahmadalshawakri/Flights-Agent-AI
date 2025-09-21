from langchain_core.runnables import RunnableLambda

def _oos_text(state: dict) -> dict:
    return {
        "output": "I’m set up to help with flights. Try one of these:",
        "context": state.get("context", {}),
    }

def _small_talk_text(state: dict) -> dict:
    return {
        "output": "Hi! Want me to find flights AMM → DOH for you?",
        "context": state.get("context", {}),
    }

OutOfScopeResponder = RunnableLambda(_oos_text)
SmallTalkResponder = RunnableLambda(_small_talk_text)
