from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

from ollama import Message
from typing_extensions import Any


class ChatMessageRole(Enum):
    user = "user"
    system = "system"
    assistant = "assistant"


@dataclass
class OllamaModel:
    name: str | None
    size_MB: int | None
    family: str | None
    format: str | None
    parameters: str | None
    quantization: str | None


@dataclass
class ContextFile:
    path: str


@dataclass
class TextFile(ContextFile):
    text: str


@dataclass
class BinaryFile(ContextFile):
    pass


class ToolTag(Enum):
    TEMPORAL = "TEMPORAL"
    SEARCH = "SEARCH"
    MATHEMATICS = "MATHEMATICS"
    ARITHMETIC = "ARITHMETIC"
    INTERNET = "INTERNET"


@dataclass
class Tool:
    name: str
    function: Callable
    tags: list[ToolTag]


@dataclass
class RawPromptRequest:
    system_prompt: str
    user_prompt: list[str]
    tools: list[Tool]
    message_history: list[dict[str, Any]] = field(default_factory=lambda: list())


@dataclass
class PromptStats:
    model: str
    done_reason: str | None
    total_duration_s: float
    load_duration_ms: float
    prompt_eval_count: int
    prompt_eval_duration_s: float
    eval_count: int
    eval_duration_s: float

    @property
    def tokens_in_per_second(self):
        return (self.prompt_eval_count / self.prompt_eval_duration_s) if self.prompt_eval_duration_s != 0 else 9

    @property
    def tokens_out_per_second(self):
        return (self.eval_count / self.eval_duration_s) if self.eval_duration_s != 0 else 0


@dataclass
class RawPromptResponse:
    content: str
    thinking: str
    tool_calls: list[Message.ToolCall]
    message_history: list[dict[str, str]]
    stats: PromptStats | None

    failed: bool = field(default=False)
    failure_error: str = field(default="")
    failure_stacktrace: str = field(default="")
