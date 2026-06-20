from dataclasses import dataclass
from enum import Enum


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


@dataclass
class RawPromptRequest:
    system_prompt: str
    user_prompt: list[str]


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
        return self.prompt_eval_count / self.prompt_eval_duration_s

    @property
    def tokens_out_per_second(self):
        return self.eval_count / self.eval_duration_s


@dataclass
class RawPromptResponse:
    content: str
    thinking: str
    stats: PromptStats | None
