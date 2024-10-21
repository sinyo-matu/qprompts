from enum import StrEnum
from pydantic import BaseModel, Field
from typing import Any, Optional, Literal
from jinja2 import Template


class ModelConfiguration(BaseModel):
    type: Literal["openai", "anthropic", "cohere"]
    name: str


class ModelParameters(BaseModel):
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None


class Model(BaseModel):
    api: Literal["chat", "completion"]
    configuration: ModelConfiguration
    parameters: ModelParameters


class ChatRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"


class ChatMessage(BaseModel):
    role: ChatRole
    text: str


class PromptStructure(BaseModel):
    name: str
    description: Optional[str] = None
    authors: list[str] = Field(default_factory=list)
    model: Model
    sample: dict[str, Any] = Field(default_factory=dict)
    body: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()

    def render_sample(self, **kwargs) -> list[ChatMessage]:
        chat_history = self.sample.get("chat_history", {})
        return [
            ChatMessage(role=ChatRole(role), text=Template(content).render(**kwargs))
            for role, content in chat_history.items()
        ]

    def render_body(self, **kwargs) -> list[ChatMessage]:
        return [
            ChatMessage(role=ChatRole(key), text=Template(content).render(**kwargs))
            for key, content in self.body.items()
        ]
