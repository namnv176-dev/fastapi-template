from collections.abc import AsyncGenerator
from dataclasses import dataclass
from pydantic import BaseModel, Field, field_validator
from typing import Any
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser, JsonOutputParser

from src.core.config import settings
from src.db.models.chat import ChatMessage
from src.infrastructure.llm.factory import llm_factory
from src.infrastructure.llm.guardrails import guardrails

try:
    import tiktoken
except ImportError:
    tiktoken = None  # type: ignore



class LLMHandler:
    def __init__(self, provider: str | None = None, model: str | None = None) -> None:
        self._provider = provider or settings.LLM_PROVIDER
        self._model = model or settings.LLM_MODEL
        self._llm = llm_factory.get_llm(provider=self._provider, model=self._model)

    def _get_encoding(self) -> Any:
        if not tiktoken:
            return None
        try:
            return tiktoken.encoding_for_model(self._model)
        except (KeyError, Exception):
            return tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        if self._provider == "openai" and tiktoken:
            encoding = self._get_encoding()
            if encoding:
                return len(encoding.encode(text))
        return len(text) // 4

    async def chat(
        self,
        message_content: str,
        history: list[ChatMessage],
        system_prompt: str | None = None,
        streaming: bool = True,
        structured_output: dict | None = None,
    ) -> AsyncGenerator[dict[str, Any], None] | dict[str, Any]:
        """
        Interact with LLM using a pre-fetched history list.
        Usage metadata is extracted from LLM response instead of manual calculation.
        """
        guardrails.validate_input(message_content)

        messages = self._prepare_messages(history, message_content, system_prompt)

        if structured_output:
            return await self._invoke_response(messages, structured_output)

        if streaming:
            return self._stream_response(messages)
        return await self._invoke_response(messages)

    def _prepare_messages(
        self, history: list[ChatMessage], content: str, system_prompt: str | None
    ) -> list[BaseMessage]:
        """Maps ChatMessage models to LangChain messages."""
        langchain_msgs: list[BaseMessage] = []
        if system_prompt:
            langchain_msgs.append(SystemMessage(content=system_prompt))

        # Map history
        role_map = {"human": HumanMessage, "ai": AIMessage, "system": SystemMessage}
        for m in history:
            if m.role in role_map:
                langchain_msgs.append(role_map[m.role](content=m.content))

        # Add current human message (saving to DB happens in the Service layer)
        langchain_msgs.append(HumanMessage(content=content))
        return langchain_msgs

    async def _stream_response(self, messages: list[BaseMessage]) -> AsyncGenerator[dict[str, Any], None]:
        """Streams content and usage metadata from the LLM."""
        async for chunk in self._llm.astream(messages):
            content = chunk.content
            if isinstance(content, str) and content:
                yield {"type": "content", "content": content}

            # # Extract usage metadata (available in the final chunk if supported by provider)
            if hasattr(chunk, "usage_metadata") and chunk.usage_metadata:
                yield {"type": "usage", "usage": chunk.usage_metadata}

    async def _invoke_response(
        self, messages: list[BaseMessage], structured_output: type[BaseModel] | None = None
    ) -> dict[str, Any]:
        """Gets full content response and usage metadata from the LLM."""
        if structured_output:
            response = await self._llm.with_structured_output(
                structured_output, 
            ).ainvoke(messages)
            return response
        else:
            response = await self._llm.ainvoke(messages)
            content = str(response.content)
            guardrails.validate_output(content)
            usage = getattr(response, "usage_metadata", None)
            return {"content": content, "usage": usage}

    
llm_handler = LLMHandler()


if __name__ == "__main__":
    import asyncio

    llm_handler = LLMHandler()
    system_prompt = "You are a helpful assistant about technology."

    async def main():
        response = await llm_handler.chat("Hello, what is the capital of usa? tell me about the country.", [], system_prompt=system_prompt, structured_output=ComplaintExtraction)
        async for chunk in response:
            if chunk['type'] == 'content':
                print(chunk['content'], end="")
        print("\n")
    asyncio.run(main())
