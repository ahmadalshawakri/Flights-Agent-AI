from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from .tools import search_offers_tool, price_offer_tool, create_order_tool

def build_agent():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    tools = [search_offers_tool, price_offer_tool, create_order_tool]
    system = (
        "You are a flight assistant. When the user asks to find flights, "
        "CALL the tool `search_offers` with these fields when known: "
        "originLocationCode, destinationLocationCode, departureDate, returnDate, "
        "adults, travelClass, nonStop, currencyCode, max. "
        "Infer IATA codes from city names when unambiguous (Amman→AMM, Doha→DOH). "
        "If required fields are missing, ask ONE clarifying question; do NOT call "
        "the tool with empty or partial arguments."
    )
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=False,
        handle_parsing_errors=True,
        agent_kwargs={"system_message": system},
    )
    return agent
