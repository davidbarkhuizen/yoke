from dataclasses import dataclass
from enum import Enum


class ChatMessageRole(Enum):
    user = "user"
    system = "system"
    assistant = "assistant"


@dataclass
class CommunicationStats:
    model: str
    done_reason: str | None
    total_duration_s: float
    load_duration_ms: float
    prompt_eval_count: int
    prompt_eval_duration_s: float
    eval_count: int
    eval_duration_s: float


@dataclass
class CommunicationResponse:
    content: str
    thinking: str
    stats: CommunicationStats | None


@dataclass
class OllamaModel:
    name: str | None
    size_MB: int | None
    family: str | None
    format: str | None
    parameters: str | None
    quantization: str | None


@dataclass
class TextFile:
    path: str
    contents: str
