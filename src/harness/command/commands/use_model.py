from typing import Callable

from ollama import AsyncClient
from rich.console import Console

from config import YokeConfig
from harness.command.abstract import AbstractHarnessCommand
from markdown.display import display_text_as_markdown


class UseModelCommand(AbstractHarnessCommand):
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
        return "use-model"

    @property
    def usage(self) -> str:
        return "use-model [model]"

    async def execute(self, model: str, args: list[str]) -> bool:

        if len(args) != 1:
            display_text_as_markdown(self.console, self.usage)
            return False

        _new_model: str = args[0]
        return self._switch_model(_new_model)
