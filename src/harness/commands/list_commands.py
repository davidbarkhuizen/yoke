from harness.commands.abstract import AbstractHarnessCommand
from markdown.display import display_text_as_markdown
from markdown.render import dict_list_to_markdown_table


class ListCommandsCommand(AbstractHarnessCommand):
    @property
    def command(self) -> str:
        return "list-commands"

    async def execute(self, model: str, think: bool, args: list[str]) -> bool:

        model_dicts = [{"command": command.command, "usage": command.usage} for command in self.commands]
        model_dicts = sorted(model_dicts, key=lambda d: d["command"])

        display_text_as_markdown(self.console, dict_list_to_markdown_table(model_dicts))

        return True
