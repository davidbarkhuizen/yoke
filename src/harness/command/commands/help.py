from ollama import AsyncClient
from rich.console import Console
from typing_extensions import Sequence

from config import YokeConfig
from harness.command.abstract import AbstractHarnessCommand
from markdown.display import display_text_as_markdown
from markdown.render import dict_list_to_markdown_table


class HelpCommand(AbstractHarnessCommand):
    def __init__(
        self,
        config: YokeConfig,
        async_client: AsyncClient,
        console: Console,
        commands: Sequence[AbstractHarnessCommand],
    ):
        super().__init__(config, async_client, console)
        self._commands = commands

    @property
    def command(self) -> str:
        return "help"

    async def execute(self, model: str, args: list[str]) -> bool:

        model_dicts = [{"command": command.command, "usage": command.usage} for command in self._commands]
        model_dicts = sorted(model_dicts, key=lambda d: d["command"])

        display_text_as_markdown(self.console, "```----------------------------------------```")
        display_text_as_markdown(self.console, "```Yoke LLM Harness. 2026. David Barkhuizen```")
        display_text_as_markdown(self.console, "```----------------------------------------```")

        display_text_as_markdown(self.console, dict_list_to_markdown_table(model_dicts, alignment="left"))

        return True
