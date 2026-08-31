from devpilot.config.settings import settings
from devpilot.services.llm_service import LLMService
from devpilot.services.openai_llm_service import OpenAILLMService


def create_llm_service() -> LLMService:
    provider = settings.llm_provider.lower()

    if provider == "openai":
        return OpenAILLMService(
            model=settings.llm_model,
            api_key=settings.openai_api_key,
        )

    raise ValueError(
        f"Unsupported LLM provider: {settings.llm_provider}"
    )