from typing import Any

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from src.core.config import settings


class OpenAICompatibleModel(OpenAIModel):
    """
    Subclass of OpenAIModel that skips strict validation of the LLM response.
    This is necessary because some providers (like Groq) return non-standard
    values in fields like 'service_tier' (e.g. 'on_demand'), which makes
    pydantic-ai's strict validation fail.
    """
    def _validate_completion(self, response: Any) -> Any:
        # Override to skip strict ChatCompletion.model_validate
        return response


class PydanticAIFactory:
    @staticmethod
    def get_model(
        model: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
    ) -> OpenAIModel:
        """
        Create a pydantic-ai OpenAI model.
        Uses Groq as the default base_url if set in the existing factory logic.
        """
        model_name = model or settings.LLM_MODEL
        
        # Following the pattern in src/infrastructure/llm/factory.py
        # which uses Groq as an OpenAI-compatible provider
        default_base_url = "https://api.groq.com/openai/v1"
        
        final_base_url = base_url or default_base_url
        final_api_key = api_key or (settings.OPENAI_API_KEY.get_secret_value() if settings.OPENAI_API_KEY else None)
        
        # In pydantic-ai 1.x, we use OpenAIProvider for custom base_url/api_key
        # and our subclass to avoid strict validation errors from non-standard fields.
        return OpenAICompatibleModel(
            model_name=model_name,
            provider=OpenAIProvider(
                base_url=final_base_url,
                api_key=final_api_key,
            ),
        )


pydantic_ai_factory = PydanticAIFactory()
