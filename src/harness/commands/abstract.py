from __future__ import annotations

from abc import ABC, abstractmethod

from ollama import AsyncClient
from rich.console import Console

from config import YokeConfig


class AbstractHarnessCommand(ABC):
    def __init__(
        self,
        config: YokeConfig,
        async_client: AsyncClient,
        console: Console,
    ):
        self.config: YokeConfig = config
        self.client: AsyncClient = async_client
        self.console: Console = console

    @property
    @abstractmethod
    def command(self) -> str:
        raise NotImplementedError()

    @property
    def usage(self) -> str:
        return self.command

    @abstractmethod
    async def execute(self, model: str, args: list[str]) -> bool:
        raise NotImplementedError()
