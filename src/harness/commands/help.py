from harness.commands.abstract import AbstractHarnessCommand
from markdown.display import display_text_as_markdown


class HelpCommand(AbstractHarnessCommand):
    @property
    def command(self) -> str:
        return "help"

    async def execute(self, model: str, args: list[str]) -> bool:

        display_text_as_markdown(self.console, "```----------------------------------------```")
        display_text_as_markdown(self.console, "```Yoke LLM Harness. 2026. David Barkhuizen```")
        display_text_as_markdown(self.console, "```----------------------------------------```")

        display_text_as_markdown(self.console, "list-commands to get a list of commands")
        return True
