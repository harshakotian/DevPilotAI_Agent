from abc import ABC, abstractmethod
from typing import Type, TypeVar

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class LLMService(ABC):
    @abstractmethod
    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        output_model: Type[T],
    ) -> T:
        """
        Generate structured output validated against a Pydantic model.
        """
        raise NotImplementedError