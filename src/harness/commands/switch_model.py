from typing import Callable

from ollama import AsyncClient
from rich.console import Console
from typing_extensions import Sequence

from config import YokeConfig
from harness.commands.abstract import AbstractHarnessCommand


class SwitchModelCommand(AbstractHarnessCommand):
    def __init__(
        self,
        config: YokeConfig,
        async_client: AsyncClient,
        console: Console,
        switch_model: Callable[[str], bool],
    ):
        super().__init__(config, async_client, console)
        self._switch_model = switch_model

    @property
    def command(self) -> str:
        return "switch-model"

    async def execute(self, model: str, args: list[str]) -> bool:

        _new_model: str = args[0]
        return self._switch_model(_new_model)
