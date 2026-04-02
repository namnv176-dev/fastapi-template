from pydantic_ai import Agent
from src.infrastructure.pydantic.factory import pydantic_ai_factory

# Simple generic agent for chat
def create_chat_agent(
    system_prompt: str | None = None,
    model: str | None = None,
) -> Agent:
    """
    Creates a new pydantic-ai Agent configured for general-purpose chat.
    Uses the factory to get an OpenAI model.
    """
    model_obj = pydantic_ai_factory.get_model(model=model)
    
    agent = Agent(
        model_obj,
        system_prompt=system_prompt or "You are a helpful, senior-level AI assistant.",
    )
    
    return agent
