from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from src.core.config import settings


class LLMFactory:
    @staticmethod
    def get_llm(
        provider: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        streaming: bool | None = None,
        **kwargs: Any,
    ) -> BaseChatModel:
        provider = provider or settings.LLM_PROVIDER
        model = model or settings.LLM_MODEL
        temperature = temperature if temperature is not None else settings.LLM_TEMPERATURE
        max_tokens = max_tokens if max_tokens is not None else settings.LLM_MAX_TOKENS
        streaming = streaming if streaming is not None else settings.LLM_STREAMING

        if provider == "openai":
            return ChatOpenAI(
                model=model,
                api_key=settings.OPENAI_API_KEY,
                temperature=temperature,
                max_completion_tokens=max_tokens,
                streaming=streaming,
                stream_options={"include_usage": True},
                base_url="https://api.groq.com/openai/v1",
                **kwargs,
            )
        elif provider == "gemini":
            return ChatGoogleGenerativeAI(
                model=model,
                google_api_key=settings.GEMINI_API_KEY,
                temperature=temperature,
                max_output_tokens=max_tokens,
                streaming=streaming,
                **kwargs,
            )
        elif provider == "anthropic":
            # For Anthropic, recent versions use model and api_key, but older use model_name
            # and may require specific names. We try model and api_key first, or fallback names.
            return ChatAnthropic(
                model_name=model,
                api_key=settings.ANTHROPIC_API_KEY if settings.ANTHROPIC_API_KEY else SecretStr(""),
                temperature=temperature,
                max_tokens_to_sample=max_tokens if max_tokens is not None else 1024,
                streaming=streaming,
                **kwargs,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")


llm_factory = LLMFactory()
