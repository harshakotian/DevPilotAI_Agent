from typing import Type, TypeVar

from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from devpilot.services.llm_service import LLMService


T = TypeVar("T", bound=BaseModel)


class OpenAILLMService(LLMService):
    def __init__(
        self,
        model: str,
        api_key: str,
        temperature: float = 0.0,
    ):
        self._client = ChatOpenAI(
            model=model,
            api_key=api_key,
            temperature=temperature,
        )

    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        output_model: Type[T],
    ) -> T:
        structured_client = self._client.with_structured_output(
            output_model
        )

        messages = [
            (
                "system",
                system_prompt,
            ),
            (
                "human",
                user_prompt,
            ),
        ]

        result = structured_client.invoke(messages)

        return result