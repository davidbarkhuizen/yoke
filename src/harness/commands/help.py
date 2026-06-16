from harness.commands.abstract import AbstractHarnessCommand
from markdown.display import display_text_as_markdown


class HelpCommand(AbstractHarnessCommand):
    @property
    def command(self) -> str:
        return "help"

    async def execute(self, model: str, think: bool, args: list[str]) -> bool:

        display_text_as_markdown(self.console, "```----------------------------------------```")
        display_text_as_markdown(self.console, "```Yoke LLM Harness. 2026. David Barkhuizen```")
        display_text_as_markdown(self.console, "```----------------------------------------```")

        list_commands_command = next(iter([c for c in self.commands if c.command == "list-commands"]))
        await list_commands_command.execute(model, think, [])

        return True
