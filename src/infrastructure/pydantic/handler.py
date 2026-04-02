from collections.abc import AsyncGenerator
from typing import Any

from pydantic_ai import Agent
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    RetryPromptPart,
    SystemPromptPart,
    TextPart,
    UserPromptPart,
)

from src.db.models.chat import ChatMessage
from src.infrastructure.pydantic.factory import pydantic_ai_factory
from src.infrastructure.pydantic.guardrails import guardrails


class PydanticAIHandler:
    def __init__(self, model: str | None = None) -> None:
        self._model = pydantic_ai_factory.get_model(model=model)

    def _prepare_messages(
        self, history: list[ChatMessage], system_prompt: str | None = None
    ) -> list[ModelMessage]:
        """Maps ChatMessage models to pydantic-ai ModelMessage objects."""
        messages: list[ModelMessage] = []
        
        if system_prompt:
            messages.append(ModelRequest(parts=[SystemPromptPart(content=system_prompt)]))

        for m in history:
            if m.role == "human":
                messages.append(ModelRequest(parts=[UserPromptPart(content=m.content)]))
            elif m.role == "ai":
                messages.append(ModelResponse(parts=[TextPart(content=m.content)]))
            elif m.role == "system":
                messages.append(ModelRequest(parts=[SystemPromptPart(content=m.content)]))
        
        return messages

    async def chat(
        self,
        message_content: str,
        history: list[ChatMessage],
        system_prompt: str | None = None,
        streaming: bool = True,
    ) -> AsyncGenerator[dict[str, Any], None] | dict[str, Any]:
        """
        Interact with LLM using pydantic-ai.
        """
        # Validate Input
        guardrails.validate_input(message_content)

        # Create an agent for this interaction
        agent = Agent(self._model, system_prompt=system_prompt)
        
        # Prepare message history
        message_history = self._prepare_messages(history)

        if streaming:
            return self._stream_response(agent, message_content, message_history)
        return await self._invoke_response(agent, message_content, message_history)

    async def _stream_response(
        self, agent: Agent, content: str, history: list[ModelMessage]
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Streams content using agent.run_stream."""
        async with agent.run_stream(content, message_history=history) as result:
            async for chunk in result.stream_text(delta=True):
                # Yield content in the format the UI/Service expects
                # Note: chunk here is the incremental text part? 
                # Actually pydantic-ai streams "full text so far" or "chunks"?
                # stream_text() yields chunks of text by default.
                yield {"type": "content", "content": chunk}
            
            # To get usage, we need to access result.usage() after the stream is finished
            usage = result.usage()
            yield {
                "type": "usage",
                "usage": {
                    "input_tokens": usage.input_tokens,
                    "output_tokens": usage.output_tokens,
                    "total_tokens": usage.total_tokens,
                },
            }

    async def _invoke_response(
        self, agent: Agent, content: str, history: list[ModelMessage]
    ) -> dict[str, Any]:
        """Gets full content response using agent.run."""
        result = await agent.run(content, message_history=history)
        
        # Validate Output
        guardrails.validate_output(result.output)

        usage = result.usage()
        return {
            "content": result.output,
            "usage": {
                "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens,
                "total_tokens": usage.total_tokens,
            },
        }

if __name__ == "__main__":
    import asyncio

    async def main():
        handler = PydanticAIHandler()
        
        print("Testing Invoke:")
        response = await handler.chat(
            "Hello, what is the capital of Vietnam?", 
            [], 
            system_prompt="You are a helpful assistant about technology.", 
            streaming=False
        )
        print(f"Invoke Result: {response}")
        
        print("\nTesting Stream:")
        stream = await handler.chat(
            "Hello, what is the capital of usa? tell me about the country.", 
            [], 
            system_prompt="You are a helpful assistant about technology.", 
            streaming=True
        )
        async for chunk in stream:
            print(f"Stream Chunk: {chunk}")

    asyncio.run(main())